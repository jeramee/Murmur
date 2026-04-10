---
declare: workflow
name: refrain_guard
---

# Refrain guard

Demonstrate deliberate non-action followed by a visible halt.

```yaml
steps:
  - id: announce_gate
    utter:
      value: Checking the gate.

  - id: deliberate_pause
    refrain:
      mode: skip
      reason: pause here on purpose

  - id: halt_workflow
    refrain:
      mode: halt
      reason: demonstration complete

  - id: unreachable_notice
    utter:
      value: You should not see this line.
```