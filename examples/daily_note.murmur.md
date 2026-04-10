---
declare: workflow
name: daily_note
inputs:
  title: text
  body: text
  publish: boolean
---

# Daily note

Trim the body text, mark it as draft or published, store a note, and announce where it landed.

```yaml
steps:
  - id: distill_body
    distill:
      value: ${inputs.body}
      mode: strip
      into: clean_body

  - id: optional_pause
    refrain:
      mode: skip
      reason: placeholder for a deliberate no-op

  - id: choose_suffix
    choose:
      from:
        - when: ${inputs.publish}
          value: published
      default: draft
      into: note_kind

  - id: compose_note
    weave:
      pattern: "# {title}\n\nstatus: {kind}\n\n{body}\n"
      with:
        title: ${inputs.title}
        kind: ${note_kind}
        body: ${clean_body}
      into: rendered_note

  - id: save_note
    store:
      to: file
      path: output/${inputs.title}.md
      value: ${rendered_note}
      mode: overwrite
      into: written_path

  - id: witness_note
    witness:
      label: note-path
      value: ${written_path}
      to: trace

  - id: announce_note
    utter:
      value: Wrote ${note_kind} note to ${written_path}
```