# Murmur Syntax Spec v0

Murmur v0 is a Markdown document with a constrained YAML shape.

The design principle is simple:

- Markdown carries human intent, framing, explanation, and narrative structure.
- YAML carries machine-readable declarations and executable structure.
- The runtime executes YAML, but may preserve Markdown for diagnostics, help, trace output, and tooling.

This spec is formal-ish by design. It aims to make Murmur implementable without pretending the language is already frozen.

## 1. File model

A Murmur source file is a UTF-8 text file, usually using the extension `.murmur.md`.

A valid Murmur document has three layers:

1. Optional YAML front matter at the top of the file.
2. Ordinary Markdown body.
3. Zero or more fenced YAML blocks inside the Markdown body that declare executable structures.

Canonical shape:

```md
---
declare: workflow
name: greet_visitor
inputs:
  visitor: text
---

# Greet visitor

Purpose: prepare a greeting.

```yaml
steps:
  - name: weave greeting
    weave:
      pattern: "Hello, {visitor}."
      with:
        visitor: ${inputs.visitor}
      into: greeting

  - name: utter greeting
    utter:
      value: ${greeting}
```
```

## 2. Lexical and structural rules

### 2.1 Encoding and line endings

- Source files MUST be valid UTF-8.
- Runtimes SHOULD accept both LF and CRLF line endings.
- Parsers SHOULD normalize line endings internally.

### 2.2 Top-level document structure

A Murmur document MAY begin with YAML front matter delimited by `---` on its own line.

If front matter is present:

- it MUST be the first construct in the file
- it MUST end with a second `---` line
- it MUST parse as a YAML mapping

Everything after front matter is Markdown body.

### 2.3 Executable YAML blocks

Executable content lives inside fenced code blocks whose info string is `yaml` or `yml`.

A runtime MAY ignore non-YAML code blocks.

A YAML fence is considered executable Murmur YAML when its root node is a mapping that contains one or more recognized Murmur keys such as:

- `steps`
- `branch`
- `loop`
- `handlers`
- command invocations in normalized step form

Tooling MAY preserve unknown YAML blocks as inert documentation blocks.

## 3. Semantic layers

Murmur has four semantic layers.

### 3.1 Metadata layer

Front matter declares document identity and interface information.

Typical keys:

- `declare`: kind of document, usually `workflow`
- `name`: stable workflow name
- `version`: optional document version
- `inputs`: input schema or input names
- `outputs`: declared outputs
- `requires`: capabilities, tools, or environmental assumptions

Example:

```yaml
declare: workflow
name: greet_visitor
version: 0
inputs:
  visitor: text
  mood:
    type: text
    required: false
```

### 3.2 Narrative layer

Markdown headings, paragraphs, lists, tables, and callouts provide explanation for humans.

The runtime is not required to execute narrative text, but tooling SHOULD preserve it for:

- trace display
- generated documentation
- editor assistance
- AI-assisted authoring
- operator context

### 3.3 Executable layer

Executable YAML blocks define steps, control flow, data flow, and side effects.

### 3.4 Reference layer

String interpolation and variable references connect steps to document state.

## 4. Data model

Murmur values are YAML values plus runtime-resolved references.

Core value kinds:

- `null`
- boolean
- number
- text
- sequence
- mapping

Runtimes MAY support richer values internally, but the portable surface area for v0 is the YAML data model.

## 5. Environment and scope

Execution occurs within an environment of named bindings.

Minimum well-known scopes:

- `inputs.*`: values provided from the caller
- `meta.*`: normalized front matter metadata
- local step outputs: values previously bound by `into`
- runtime context, if exposed, under implementation-defined namespaces

Prototype note: the starter Python runtime currently exposes `inputs.*`, `meta.*`, `${steps.some_id.output}`, and local variables bound with `into`.

A reference like `${inputs.visitor}` reads from the environment.

A write target like `into: greeting` binds a new local value named `greeting`.

### 5.1 Binding rules

- Bindings are created in execution order.
- Later bindings with the same name SHOULD shadow earlier local bindings in the current workflow scope.
- Implementations MAY reject accidental rebinding in strict mode.

## 6. References and interpolation

Murmur v0 uses `${...}` as its canonical reference syntax.

Examples:

- `${inputs.visitor}`
- `${greeting}`
- `${meta.name}`

### 6.1 Reference grammar

Informal grammar:

```text
reference     := '${' path '}'
path          := segment ('.' segment)*
segment       := [A-Za-z_][A-Za-z0-9_\-]*
```

### 6.2 Interpolation behavior

A plain scalar string MAY contain zero or more embedded references.

Example:

```yaml
pattern: "Good evening, {visitor}."
with:
  visitor: ${inputs.visitor}
```

Portable v0 runtimes SHOULD support two modes:

1. pure reference value mode, where the entire scalar is `${...}` and resolves to the referenced value as-is
2. string interpolation mode, where `${...}` appears within a larger string and resolves via stringification

If a reference cannot be resolved, the runtime SHOULD raise a structured execution error unless the command defines fallback behavior.

## 7. Workflow normalization

Runtimes SHOULD normalize executable YAML into a common internal representation.

Canonical normalized step shape:

```yaml
- name: <optional human label>
  <command-name>:
    ...command arguments...
```

Example:

```yaml
- name: utter greeting
  utter:
    value: ${greeting}
```

A step is therefore a mapping with optional metadata keys and exactly one command key.

Reserved step metadata keys for v0:

- `name`
- `if`
- `id`
- `note`
- `expects`

Implementations MAY add more metadata keys, but portable documents SHOULD avoid unstandardized metadata unless guarded by tooling conventions.

## 8. Commands

A command is an operation identified by a verb-like key such as `weave`, `utter`, `heed`, `turn`, or `distill`.

This syntax spec does not freeze the whole command dictionary, but it defines the invocation contract.

### 8.1 Invocation contract

A command invocation is a mapping whose key is the command name and whose value is either:

- a mapping of named arguments, or
- a scalar shorthand, if that command defines one

Preferred portable form is named-argument mapping.

Example:

```yaml
- weave:
    pattern: "Hello, {visitor}."
    with:
      visitor: ${inputs.visitor}
    into: greeting
```

### 8.2 Side effects

Commands that produce visible side effects, such as speaking, file writes, network actions, or shell execution, SHOULD make those effects explicit in their argument structure.

Murmur prefers visible ceremony over hidden magic.

## 9. Control flow

Murmur v0 supports structured control flow through YAML forms rather than punctuation-heavy syntax.

### 9.1 Sequential flow

A `steps` sequence executes in order.

```yaml
steps:
  - weave:
      pattern: "Hello"
      into: greeting
  - utter:
      value: ${greeting}
```

### 9.2 Conditional execution

A step MAY define `if` to guard execution.

```yaml
- name: utter only when enabled
  if: ${inputs.enabled}
  utter:
    value: "Proceeding"
```

`if` is truth-tested according to YAML-like truthiness or a stricter runtime-defined boolean policy.
Portable runtimes SHOULD document their coercion rules.

### 9.3 Branching

A branch form MAY be represented explicitly:

```yaml
branch:
  when:
    - if: ${inputs.formal}
      steps:
        - utter:
            value: "Good evening."
  else:
    steps:
      - utter:
          value: "Hey there."
```

Portable v0 guidance:

- `when` is an ordered list of guarded arms
- first truthy arm wins
- optional `else` runs if no arm matches

### 9.4 Loops

A loop form MAY be represented as:

```yaml
loop:
  for: item in ${inputs.items}
  steps:
    - utter:
        value: ${item}
```

Portable v0 runtimes MAY instead expose iteration through commands, but if structural loops are supported, they SHOULD preserve block-scoped iteration bindings.

## 10. Error semantics

Murmur distinguishes parse errors from execution errors.

### 10.1 Parse errors

A parse error occurs when:

- front matter is malformed
- an executable YAML block is invalid YAML
- a required structural form is not well-formed

### 10.2 Validation errors

A validation error occurs when the document parses but violates Murmur structural rules.

Examples:

- a step has zero commands
- a step has multiple command keys
- `steps` is not a sequence
- `inputs` is neither a mapping nor other supported schema form

### 10.3 Execution errors

An execution error occurs when:

- a reference cannot be resolved
- a command fails
- a side effect is denied or unavailable
- a type expectation is violated at runtime

Runtimes SHOULD report:

- document path
- line or fence location when available
- step name or step index when available
- command name
- concise reason

## 11. Markdown interaction rules

Markdown is not dead weight. It is part of the language surface.

Portable tooling SHOULD preserve associations between executable blocks and their surrounding Markdown context, especially:

- nearest heading
- preceding paragraphs
- block captions or admonitions

This allows a runtime or editor to display things like:

- “Running step block under `## Prepare greeting`”
- “Purpose: prepare a greeting and speak it”

Markdown does not directly alter execution in v0 unless a tool deliberately projects it into metadata.

## 12. Input and output contracts

### 12.1 Inputs

`inputs` in front matter defines the named external interface.

Portable v0 input forms:

```yaml
inputs:
  visitor: text
  mood: text
```

or

```yaml
inputs:
  visitor:
    type: text
    required: true
  mood:
    type: text
    default: calm
```

### 12.2 Outputs

`outputs` MAY declare workflow result names.

```yaml
outputs:
  greeting: text
```

The precise return mechanism is runtime-defined in v0, but portable runtimes SHOULD make declared outputs inspectable.

## 13. Minimal conformance profile for v0

A minimal Murmur v0 implementation SHOULD:

1. parse optional front matter
2. parse Markdown body
3. discover YAML fenced blocks
4. identify executable blocks
5. execute sequential `steps`
6. resolve `${...}` references
7. bind `into` outputs into workflow scope
8. emit structured errors

A stronger implementation MAY also support:

- conditional `if`
- explicit `branch`
- structural `loop`
- source span tracking
- documentation-aware traces

## 14. Informal grammar summary

The following is descriptive, not normative YAML grammar.

```text
document         := front_matter? markdown_body
front_matter     := '---' yaml_mapping '---'
markdown_body    := markdown_node*
markdown_node    := prose | executable_yaml_fence | other_code_fence | markdown_structure
executable_yaml_fence := fenced_block(info='yaml'|'yml', content=yaml_mapping)

workflow_block   := mapping containing steps | branch | loop
steps            := 'steps' ':' sequence(step)
step             := mapping(optional_step_meta, one_command)
one_command      := command_name ':' command_args
command_args     := mapping | scalar
reference        := '${' path '}'
```

## 15. Style guidance for authors

Portable Murmur documents SHOULD:

- use clear headings
- name steps explicitly when it helps traceability
- keep side effects obvious
- prefer named arguments over terse shorthands
- keep Markdown explanatory, not ornamental noise

Murmur is at its best when the document reads well before it runs.

## 16. Non-goals for v0

This spec deliberately does not standardize:

- static typing beyond light schema hints
- package management
- modules and imports
- concurrency semantics
- distributed execution
- capability security model
- the complete command dictionary

Those can arrive later. v0 only needs a shape sturdy enough to stand.
