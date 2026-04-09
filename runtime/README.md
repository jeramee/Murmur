# Murmur runtime prototype

This starter runtime executes a `.murmur.md` document by:

1. Loading YAML frontmatter from the top of the file
2. Extracting fenced `yaml` blocks from the Markdown body
3. Executing `steps:` lists found in those blocks
4. Resolving simple references like `${inputs.name}`, `${steps.some_step.output}`, and `${variable}`

## Primitives

- `weave`: format a string pattern with values from `with`
- `utter`: print a value and record it in runtime outputs
- `write`: write content to a file path
- `distill`: lightly transform a value (`strip`, `lines`, `lower`, `keys`)

## Run

```bash
python3 runtime/murmur.py examples/greet_visitor.murmur.md --input visitor=Milord --input mood=awake
```

Use `--json` if you want the final runtime state after execution.
