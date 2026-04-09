# Murmur Command Dictionary v0

This document defines the **v0 command vocabulary** for Murmur.

Its job is to make the language small, legible, and executable while still leaving room for expressive naming and AI-assisted authoring.

Murmur commands fall into two broad families:

1. **Deterministic core commands**: stable runtime primitives with exact semantics.
2. **Fuzzy or AI-facing commands**: intentionally softer commands whose implementation may involve ranking, interpretation, synthesis, or model assistance.

For v0, deterministic commands are the real foundation. Fuzzy commands are allowed, but must degrade gracefully, remain inspectable, and never erase the visible shape of execution.

## Design goals

The command set should:

- feel like procedure written as notes
- sound descriptive, expressive, and slightly haunted
- map cleanly onto a tiny runtime
- keep side effects visible
- support both hand-authored and AI-assisted documents
- distinguish exact execution from interpretive execution

## Command shape

A command appears as a YAML mapping inside a step.

Example:

```yaml
- name: weave greeting
  weave:
    pattern: "Hello, {name}."
    with:
      name: ${inputs.name}
    into: greeting
```

A step should normally contain one primary command. Supporting metadata like `name`, `when`, `on_error`, `timeout`, or `tags` may appear beside it.

## Standard step envelope

All commands may appear inside a common step envelope:

```yaml
- name: human-readable step name
  when: ${condition}        # optional
  timeout: 30s              # optional
  on_error: halt            # optional: halt | continue | branch
  tags: [demo, greeting]    # optional
  <command-name>:
    ...command body...
```

Common envelope semantics:

- `name`: human-facing label for logs and traces.
- `when`: execute only when truthy.
- `timeout`: maximum allowed execution duration.
- `on_error`: failure policy.
- `tags`: non-semantic labels for tooling and filtering.

## Deterministic core commands

These commands define the executable spine of Murmur v0.

### 1. `weave`

**Purpose:** Construct text, structured values, or templates from known pieces.

**Category:** deterministic

**Semantics:**

- Interpolates values into a pattern or template.
- Produces a deterministic result when the same inputs are provided.
- Does not cause external side effects by itself.

**Common fields:**

- `pattern`: format string or template source
- `with`: variable bindings
- `into`: destination variable

**Example:**

```yaml
- name: weave greeting
  weave:
    pattern: "Good evening, {visitor}."
    with:
      visitor: ${inputs.visitor}
    into: greeting
```

**Naming rationale:**
`weave` suggests assembling strands into a coherent whole. It fits Murmur's tone better than `format` while still being easy to understand.

---

### 2. `turn`

**Purpose:** Transform one value into another through a deterministic conversion.

**Category:** deterministic

**Semantics:**

- Applies an exact transformation.
- Used for casing, parsing, normalization, serialization, trimming, splitting, joining, casting, and similar operations.
- Should not imply model judgment.

**Common fields:**

- `value`: source value
- `using`: named transform or transform pipeline
- `into`: destination variable

**Example:**

```yaml
- name: normalize mood
  turn:
    value: ${inputs.mood}
    using: lowercase
    into: mood_normalized
```

**Naming rationale:**
`turn` implies changing a thing's form without changing its identity too much.

---

### 3. `distill`

**Purpose:** Reduce structured or textual input to a smaller exact result.

**Category:** deterministic by default

**Semantics:**

- Extracts, filters, reduces, or summarizes by explicit rules.
- In deterministic mode, rules must be inspectable and reproducible.
- If model assistance is used, it must be declared as fuzzy instead.

**Common fields:**

- `from`: source value
- `select`: fields, keys, or slices to retain
- `rule`: deterministic reduction rule
- `into`: destination variable

**Example:**

```yaml
- name: distill title slug
  distill:
    from: ${inputs.title}
    rule: slugify
    into: slug
```

**Naming rationale:**
`distill` evokes reduction to essence.

---

### 4. `gather`

**Purpose:** Collect values from known sources into a list or object.

**Category:** deterministic

**Semantics:**

- Reads from explicit sources.
- Produces an aggregate value.
- No hidden search.

**Common fields:**

- `from`: list of sources
- `as`: list | map
- `into`: destination variable

**Example:**

```yaml
- name: gather greeting parts
  gather:
    from:
      - ${inputs.salutation}
      - ${inputs.name}
    as: list
    into: parts
```

**Naming rationale:**
Plain, procedural, and easy to teach.

---

### 5. `choose`

**Purpose:** Select one branch or value from explicit alternatives.

**Category:** deterministic

**Semantics:**

- Evaluates explicit predicates in order.
- Uses the first matching branch unless otherwise declared.
- Equivalent in spirit to `if/else` or `switch`.

**Common fields:**

- `from`: ordered options
- `default`: fallback option
- `into`: destination variable, or nested `steps`

**Example:**

```yaml
- name: choose salutation
  choose:
    from:
      - when: ${inputs.formal}
        value: "Good evening"
      - when: ${inputs.casual}
        value: "Hey"
    default: "Hello"
    into: salutation
```

**Naming rationale:**
`choose` feels more human than `switch` while staying crisp.

---

### 6. `repeat`

**Purpose:** Iterate over values or repeat nested steps.

**Category:** deterministic

**Semantics:**

- Executes for each item in an explicit collection or for a declared count.
- Iteration order must be defined.
- Loop variables are visible and inspectable.

**Common fields:**

- `for_each`: collection
- `as`: loop variable name
- `times`: numeric repetition count
- `steps`: nested steps

**Example:**

```yaml
- name: greet all visitors
  repeat:
    for_each: ${inputs.visitors}
    as: visitor
    steps:
      - name: utter greeting
        utter:
          value: "Hello, ${visitor}"
```

**Naming rationale:**
Simple and unsurprising.

---

### 7. `utter`

**Purpose:** Emit a visible output.

**Category:** deterministic side effect

**Semantics:**

- Writes to a declared output surface such as stdout, logs, transcript, or message buffer.
- Must make the destination visible.
- Does not hide where words go.

**Common fields:**

- `value`: content to emit
- `to`: stdout | stderr | log | transcript | named sink
- `format`: text | json | yaml

**Example:**

```yaml
- name: utter final greeting
  utter:
    value: ${greeting}
    to: stdout
```

**Naming rationale:**
`utter` is theatrical and precise: something is spoken aloud into the world.

---

### 8. `heed`

**Purpose:** Read an explicit input from environment, arguments, file, or declared source.

**Category:** deterministic

**Semantics:**

- Pulls data from a named source.
- Source must be explicit.
- Runtime should expose provenance.

**Common fields:**

- `from`: input | env | file | stdin | state | secret
- `path` or `key`: source locator
- `into`: destination variable
- `required`: boolean

**Example:**

```yaml
- name: heed visitor name
  heed:
    from: input
    key: visitor
    into: visitor_name
    required: true
```

**Naming rationale:**
`heed` implies attentive intake rather than passive assignment.

---

### 9. `witness`

**Purpose:** Record state, evidence, or trace information.

**Category:** deterministic side effect

**Semantics:**

- Captures an observation for logs, audit trails, or reports.
- Should not mutate the observed value.
- May persist structured execution facts.

**Common fields:**

- `value`: value to record
- `label`: observation label
- `to`: log | trace | file | report

**Example:**

```yaml
- name: witness chosen greeting
  witness:
    label: greeting
    value: ${greeting}
    to: trace
```

**Naming rationale:**
`witness` makes observability feel explicit and ceremonial.

---

### 10. `store`

**Purpose:** Persist a value into state, file, or declared sink.

**Category:** deterministic side effect

**Semantics:**

- Writes data to a visible destination.
- Must make overwrite behavior explicit.
- Used for durable state changes.

**Common fields:**

- `value`: value to persist
- `to`: state | file | cache | output
- `path` or `key`: destination locator
- `mode`: create | overwrite | append | merge

**Example:**

```yaml
- name: store transcript
  store:
    value: ${greeting}
    to: file
    path: ./out/greeting.txt
    mode: overwrite
```

**Naming rationale:**
A plain anchor command for persistence.

---

### 11. `branch`

**Purpose:** Transfer control to another named step block, workflow, or branch.

**Category:** deterministic

**Semantics:**

- Performs explicit control redirection.
- Useful for structured subflows and error routing.
- Must target something named and inspectable.

**Common fields:**

- `to`: branch or workflow name
- `with`: argument bindings

**Example:**

```yaml
- name: branch to fallback flow
  branch:
    to: fallback_greeting
    with:
      visitor: ${inputs.visitor}
```

**Naming rationale:**
More evocative than `goto`, safer than chaos.

---

### 12. `refrain`

**Purpose:** Stop, skip, or intentionally do nothing.

**Category:** deterministic control

**Semantics:**

- Represents an intentional non-action.
- Can halt the current step, current branch, or whole workflow depending on mode.
- Makes omission visible.

**Common fields:**

- `mode`: skip | stop | halt
- `reason`: human-readable explanation

**Example:**

```yaml
- name: refrain if visitor missing
  when: ${not inputs.visitor}
  refrain:
    mode: halt
    reason: "Cannot greet an unnamed visitor."
```

**Naming rationale:**
`refrain` sounds deliberate, not accidental.

---

### 13. `invoke`

**Purpose:** Call a named external tool, routine, or runtime capability.

**Category:** deterministic if tool contract is deterministic

**Semantics:**

- Bridges Murmur to external execution.
- Capability name and arguments must be explicit.
- Side effects inherit from the invoked tool and should be surfaced.

**Common fields:**

- `tool`: named capability
- `with`: arguments
- `into`: optional captured result

**Example:**

```yaml
- name: invoke markdown renderer
  invoke:
    tool: markdown.render
    with:
      source: ${draft}
    into: rendered_html
```

**Naming rationale:**
Clear ritual language for crossing the boundary from document to machine action.

## Fuzzy and AI-facing commands

These commands are permitted in v0, but they are second-order citizens. They must be clearly marked as interpretive, and runtimes should expose prompts, confidence signals, fallback paths, and produced artifacts when possible.

## Rules for fuzzy commands

A fuzzy command should:

- declare that it is fuzzy or model-assisted
- preserve inputs and outputs for inspection
- prefer suggestion over silent mutation
- support a deterministic fallback when practical
- avoid hidden irreversible side effects

### 14. `muse`

**Purpose:** Generate candidate ideas, phrasings, plans, or options.

**Category:** fuzzy/AI

**Semantics:**

- Produces one or more suggestions.
- Output may vary between runs.
- Best used before human review or downstream filtering.

**Common fields:**

- `about`: task or topic
- `context`: supporting material
- `constraints`: guidance
- `into`: destination variable
- `count`: desired number of candidates

**Example:**

```yaml
- name: muse three greetings
  muse:
    about: polite greeting for a first-time visitor
    constraints:
      tone: warm
      length: short
    count: 3
    into: greeting_options
```

**Naming rationale:**
`muse` signals ideation rather than fact.

---

### 15. `infer`

**Purpose:** Make a best-effort judgment, classification, extraction, or interpretation.

**Category:** fuzzy/AI

**Semantics:**

- Produces an interpreted result from ambiguous input.
- Should include confidence or rationale when available.
- Appropriate for semantic labeling, intent recognition, and soft extraction.

**Common fields:**

- `from`: source material
- `task`: classification or inference description
- `schema`: expected output shape
- `into`: destination variable

**Example:**

```yaml
- name: infer visitor sentiment
  infer:
    from: ${inputs.message}
    task: classify sentiment as warm, neutral, or hostile
    schema:
      sentiment: text
      confidence: number
    into: sentiment_result
```

**Naming rationale:**
Directly marks the result as an inference, not a fact.

---

### 16. `mumble`

**Purpose:** Produce rough text or a low-confidence draft.

**Category:** fuzzy/AI

**Semantics:**

- Generates provisional output.
- Implies incompleteness or low polish.
- Useful when the workflow wants a draft before refinement.

**Common fields:**

- `about`: drafting prompt
- `style`: tone guidance
- `into`: destination variable

**Example:**

```yaml
- name: mumble a rough welcome note
  mumble:
    about: welcome note for a new contributor
    style: informal
    into: rough_note
```

**Naming rationale:**
The word itself warns the reader: this is a draft, not a decree.

---

### 17. `babble`

**Purpose:** Free-generate exploratory text or associative material.

**Category:** fuzzy/AI

**Semantics:**

- High-creativity, low-discipline generation.
- Intended for brainstorming, not direct execution-critical decisions.
- Should usually feed into `distill`, `choose`, or human review.

**Common fields:**

- `about`: topic
- `temperature`: optional creativity hint
- `into`: destination variable

**Example:**

```yaml
- name: babble tagline ideas
  babble:
    about: a haunted workflow language for notes-as-programs
    into: tagline_cloud
```

**Naming rationale:**
Openly confesses chaos. Good. Honest.

---

### 18. `slur`

**Purpose:** Approximate-match or fuzzily merge noisy input.

**Category:** fuzzy/AI or fuzzy heuristics

**Semantics:**

- Handles typo tolerance, fuzzy lookup, or rough alignment.
- Must report ambiguity if multiple matches are plausible.
- Should not silently collapse distinct meanings.

**Common fields:**

- `from`: source value
- `against`: candidate set
- `threshold`: match threshold
- `into`: destination variable

**Example:**

```yaml
- name: slur command name from noisy input
  slur:
    from: ${inputs.spoken_command}
    against: ${known_commands}
    threshold: 0.82
    into: matched_command
```

**Naming rationale:**
The unsettling name signals a blurred boundary.

---

### 19. `garble`

**Purpose:** Deliberately degrade, obfuscate, or noise a value.

**Category:** deterministic or fuzzy depending on method

**Semantics:**

- Used for corruption, redaction, masking, distortion, or robustness testing.
- Method must be explicit.
- If randomness is involved, seed control should be available.

**Common fields:**

- `value`: source value
- `using`: mask | redact | noise | scramble
- `into`: destination variable

**Example:**

```yaml
- name: garble email for logs
  garble:
    value: ${inputs.email}
    using: redact
    into: safe_email
```

**Naming rationale:**
`garble` says the output is intentionally damaged or obscured.

---

### 20. `bless`

**Purpose:** Mark a value, artifact, or branch as approved, favored, or safe to promote.

**Category:** usually deterministic, but may follow fuzzy review

**Semantics:**

- Applies a visible approval marker.
- Does not itself prove correctness unless coupled to an explicit rule.
- Useful for checkpoints and human-in-the-loop flows.

**Common fields:**

- `value`: artifact or identifier
- `as`: approval label
- `into`: optional destination

**Example:**

```yaml
- name: bless reviewed greeting
  bless:
    value: ${greeting}
    as: approved_greeting
    into: final_greeting
```

**Naming rationale:**
It sounds ceremonial, which suits promotion and approval.

## Semantic tiers

To keep Murmur sane, every command should fit one of these semantic tiers:

### Pure

No side effects. Same inputs produce same outputs.

Examples:

- `weave`
- `turn`
- `distill` (deterministic mode)
- `gather`
- `choose`

### Control

Changes flow but not the outside world directly.

Examples:

- `repeat`
- `branch`
- `refrain`

### Observable side effect

Acts on a visible output or trace surface.

Examples:

- `utter`
- `witness`
- `store`
- `invoke`

### Fuzzy or interpretive

May vary between runs or rely on model judgment.

Examples:

- `muse`
- `infer`
- `mumble`
- `babble`
- `slur`

## Command selection guidance

When authoring Murmur, prefer the most exact command that truthfully describes the step.

Use:

- `weave` when assembling known text or values
- `turn` when converting format or representation
- `distill` when reducing by rule
- `choose` when branching from explicit predicates
- `utter` when emitting output
- `witness` when recording execution evidence
- `invoke` only when crossing into external tools or capabilities
- `muse` or `babble` only when you truly want generative behavior
- `infer` only when ambiguity cannot be resolved deterministically

## Naming rules for future commands

Any future Murmur command should follow these design rules:

1. **One word only**
   - Commands should be compact and memorable.

2. **Verb-shaped**
   - A command should feel like an action.

3. **Readable in prose**
   - `utter greeting`, `witness state`, `refrain here` should sound natural.

4. **Meaning before novelty**
   - Strange is allowed. Confusing is not.

5. **Side effects should sound heavier**
   - Output and persistence commands should feel consequential.

6. **Fuzzy commands should sound fuzzy**
   - Readers should sense uncertainty from the name itself.

7. **Do not duplicate semantics under different spooky names**
   - Murmur should stay small.

8. **Default toward determinism**
   - If a command can be exact, make it exact.

9. **Keep runtime burden low**
   - Each core command should justify its existence in a tiny runtime.

10. **Preserve inspectability**
    - A reader should be able to understand roughly what happened from the document and trace.

## Anti-patterns

Avoid these mistakes in v0:

- creating multiple synonyms for the same core action
- hiding network or file side effects inside innocent-sounding pure commands
- using fuzzy commands where deterministic rules would suffice
- making AI-generated output appear authoritative without traceability
- inventing magical control flow that a reader cannot follow
- burying crucial semantics in prose instead of YAML fields

## Example mini-workflow

````md
---
declare: workflow
name: greet_visitor
inputs:
  visitor: text
  mood: text
---

# Greet visitor

```yaml
steps:
  - name: heed inputs
    heed:
      from: input
      key: visitor
      into: visitor
      required: true

  - name: normalize mood
    turn:
      value: ${inputs.mood}
      using: lowercase
      into: mood

  - name: weave greeting
    weave:
      pattern: "Good evening, {visitor}. The house is {mood}."
      with:
        visitor: ${visitor}
        mood: ${mood}
      into: greeting

  - name: witness greeting
    witness:
      label: greeting
      value: ${greeting}
      to: trace

  - name: utter greeting
    utter:
      value: ${greeting}
      to: stdout
```
````

## v0 recommendation

For the first runnable Murmur implementation, the minimum practical set is:

- `heed`
- `weave`
- `turn`
- `choose`
- `repeat`
- `utter`
- `witness`
- `store`
- `refrain`
- `invoke`

The fuzzy set can exist in the spec immediately, but may be implemented later or behind explicit runtime capabilities.

## Final principle

Murmur should read like a note written by a careful sorcerer who still believes in logs.

The document may be poetic.
The execution may not be coy.
