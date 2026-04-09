---
declare: workflow
name: step_reference_demo
inputs:
  name: text
---

# Step reference demo

Show `${steps.id.output}` resolution explicitly.

```yaml
steps:
  - id: normalize_phrase
    distill:
      value: ${inputs.name}
      mode: lower

  - id: emit_phrase
    utter:
      value: "Normalized phrase: ${steps.normalize_phrase.output}"
```
