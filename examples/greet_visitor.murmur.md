---
declare: workflow
name: greet_visitor
inputs:
  visitor: text
  mood: text
---

# Greet visitor

Prepare a greeting, then speak it.

```yaml
steps:
  - id: weave_greeting
    weave:
      pattern: "Good evening, {visitor}. The house is {mood}."
      with:
        visitor: ${inputs.visitor}
        mood: ${inputs.mood}
      into: greeting

  - id: speak_greeting
    utter:
      value: ${greeting}
```
