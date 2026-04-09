---
declare: workflow
name: daily_note
inputs:
  title: text
  body: text
---

# Daily note

Trim the body text, write a note, then announce where it landed.

```yaml
steps:
  - id: distill_body
    distill:
      value: ${inputs.body}
      mode: strip
      into: clean_body

  - id: compose_note
    weave:
      pattern: "# {title}\n\n{body}\n"
      with:
        title: ${inputs.title}
        body: ${clean_body}
      into: rendered_note

  - id: save_note
    write:
      path: output/${inputs.title}.md
      content: ${rendered_note}
      into: written_path

  - id: announce_note
    utter:
      value: Wrote note to ${written_path}
```
