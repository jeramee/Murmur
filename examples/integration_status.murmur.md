---
declare: workflow
name: integration_status
inputs: {}
---

# Check integration surfaces

Purpose: prove the shared Murmur integration boundary can address loop, settings, and calendar surfaces through one explicit command shape.

```yaml
steps:
  - name: ask loop surface for status
    invoke:
      tool: loop
      action: status
      into: loop_status

  - name: ask settings surface for status
    invoke:
      tool: settings
      action: status
      into: settings_status

  - name: ask calendar surface for status
    invoke:
      tool: calendar
      action: status
      into: calendar_status

  - name: witness integration summary
    witness:
      label: integration_status
      value:
        loop: ${loop_status}
        settings: ${settings_status}
        calendar: ${calendar_status}
      to: stdout
```
