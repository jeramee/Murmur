# Murmur

Murmur is a language disguised as procedure, and a procedure disguised as notes.

It is the mumble rap of programming: a deliberately blurred medium where code, intent, automation, and half-finished thought slur together into something strangely executable. It lives in the space between language, workflow, and invocation, where planning, prompting, scripting, and execution start to sound like the same song. 

It is a Markdown-and-YAML-based programming system where executable intent lives in human-readable documents instead of being buried inside a large opaque runtime.


Murmur should feel unclear in the best possible way at first glance: half to-do list, half ritual, half program. The runtime stays small. The documents carry the meaning.

Murmur is built on a dangerous idea: you do not need polished syntax, elite credentials, or priest-level computer science rituals to make software move. You just need to produce actionable intent with a low enough nonsense-to-signal ratio that reality starts to obey. You road the short bus to school; well my friend, you are in luck because you can still become a millionaire and maybe even a billionaire just by Murmuring non-nonsensical BS!

Start crushing it today, take your vibe coding to the next level, and leave your ops in the dust with Murmur!

## What Murmur is

- a human-readable workflow language
- a Markdown-first executable spec format
- a tiny runtime with stable primitives
- a place where notes, procedures, and programs start to blur
- a good substrate for AI-assisted authoring without making AI the sole source of truth

## What Murmur is not

- a replacement for low-level or performance-critical languages
- a pure natural-language execution engine
- a promise that ambiguity is always good
- a type-theory research project

## Core idea

In Murmur, the runtime knows how to execute.
The documents say what should happen.

That means a Murmur program can look like documentation, planning, operations, or a checklist while still being executable.

## Example

```md
---
declare: workflow
name: greet_visitor
inputs:
  visitor: text
  mood: text
---

# Greet visitor

Purpose: prepare a greeting and speak it.

```yaml
steps:
  - name: weave greeting
    weave:
      pattern: "Good evening, {visitor}. The house is {mood}."
      with:
        visitor: ${inputs.visitor}
        mood: ${inputs.mood}
      into: greeting

  - name: utter greeting
    utter:
      value: ${greeting}
```
```

## Repository map

- `docs/manifesto.md` - language concept and homepage-style copy
- `docs/command-dictionary-v0.md` - full Murmur command dictionary v0
- `docs/syntax-spec-v0.md` - formal syntax and semantic design for Murmur v0
- `examples/` - example `.murmur.md` programs
- `runtime/` - starter Python parser/runtime

## Design principles

1. Markdown carries intent, explanation, and examples.
2. YAML carries executable declarations.
3. The runtime is generic and mostly ignorant.
4. Side effects must be visible.
5. AI may assist, but specs stay authoritative.
6. Words should sound descriptive, expressive, and a little haunted.

## Command vocabulary

Murmur prefers words shaped like acts of expression, interpretation, and response.

Examples:

- `declare`
- `name`
- `weave`
- `turn`
- `distill`
- `utter`
- `heed`
- `swerve`
- `refrain`
- `witness`
- `bless`
- `babble`
- `mumble`
- `slur`
- `garble`

## Prototype status

This repository contains a starter implementation in Python. It is intentionally small and incomplete. It exists to prove the shape of the language, not to declare the design finished.

## Running the prototype

```bash
python3 runtime/murmur.py examples/greet_visitor.murmur.md --input visitor=Milord --input formal=true --input mood=awake
```

The Python prototype now covers a compact v0.1-ish slice of the language:

- value work: `weave`, `distill`
- visible output and persistence: `utter`, `write`, `store`, `witness`
- explicit intake and control flow: `heed`, `choose`, `repeat`, `refrain`
- integration boundary: `invoke` for explicit surface adapters such as loop, settings, and calendar

Examples that exercise those commands live in `examples/`, including `repeat_chorus.murmur.md`, `refrain_guard.murmur.md`, and `integration_status.murmur.md`.

## Murmur in one line

**Murmur is a language that looks like planning, reads like documentation, and executes like software.**
