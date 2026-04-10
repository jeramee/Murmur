---
declare: workflow
name: repeat_chorus
inputs:
  names: [text]
---

# Repeat chorus

Loop through a list of names, speak each line, and keep a trace.

```yaml
steps:
  - id: chorus
    repeat:
      for_each: ${inputs.names}
      as: name
      index_as: index
      steps:
        - id: line_${index}
          weave:
            pattern: "Verse {index}: hello, {name}."
            with:
              index: ${index}
              name: ${name}
            into: line

        - id: witness_${index}
          witness:
            label: chorus-line
            value: ${line}
            to: trace

        - id: utter_${index}
          utter:
            value: ${line}
```