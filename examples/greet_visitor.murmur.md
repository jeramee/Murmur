---
declare: workflow
name: greet_visitor
inputs:
  visitor: text
  formal: boolean
  mood: text
---

# Greet visitor

Prepare a greeting, choose its tone, then speak and witness it.

```yaml
steps:
  - id: pull_visitor
    heed:
      from: input
      key: visitor
      into: visitor_name
      required: true

  - id: choose_salutation
    choose:
      from:
        - when: ${inputs.formal}
          value: Good evening
      default: Hello
      into: salutation

  - id: weave_greeting
    weave:
      pattern: "{salutation}, {visitor}. The house is {mood}."
      with:
        salutation: ${salutation}
        visitor: ${visitor_name}
        mood: ${inputs.mood}
      into: greeting

  - id: witness_greeting
    witness:
      label: greeting
      value: ${greeting}
      to: trace

  - id: speak_greeting
    utter:
      value: ${greeting}
```