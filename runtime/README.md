# Murmur runtime prototype

This starter runtime executes a `.murmur.md` document by:

1. Loading YAML frontmatter from the top of the file
2. Extracting fenced `yaml` blocks from the Markdown body
3. Executing `steps:` lists found in those blocks
4. Resolving simple references like `${inputs.name}`, `${steps.some_step.output}`, `${meta.name}`, and `${variable}`

## Primitives

Implemented today, small and inspectable:

- `weave`: format a string pattern with values from `with`
- `distill`: lightly transform a value (`strip`, `lines`, `lower`, `slugify`, `keys`)
- `utter`: print a value and record it in runtime outputs
- `write`: write content to a file path
- `heed`: read from explicit sources (`input`, `env`, `file`, `state`)
- `choose`: select the first matching explicit option
- `repeat`: iterate a list or repeat by count with nested steps
- `witness`: record trace observations, optionally to stdout or a file
- `store`: persist a value to runtime state or a file
- `refrain`: make a deliberate no-op or halt visible
- `invoke`: call an explicit integration surface such as loop, settings, or calendar

## Notes

- Step-level `when:` is supported through simple truthiness checks.
- CLI `--input key=value` values are parsed as YAML scalars, so booleans, numbers, lists, and objects can be passed directly.
- The runtime is still intentionally tiny. There is no general expression language and only minimal control flow.
- External integration is now intentionally narrow: `invoke` routes through a tiny adapter registry in `runtime/integrations.py`, with stub surfaces for `loop`, `settings`, and `calendar`.

## Run

```bash
python3 runtime/murmur.py examples/greet_visitor.murmur.md --input visitor=Milord --input formal=true --input mood=awake
```

Try a looped example too:

```bash
python3 runtime/murmur.py examples/repeat_chorus.murmur.md --input 'names=["Milord", "Guest"]'
```

Use `--json` if you want the final runtime state after execution.
