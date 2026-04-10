#!/usr/bin/env bash
set -euo pipefail

python3 runtime/murmur.py examples/greet_visitor.murmur.md --input visitor=Milord --input formal=true --input mood=awake --json
python3 runtime/murmur.py examples/repeat_chorus.murmur.md --input 'names=["Milord", "Guest"]' --json
python3 runtime/murmur.py examples/daily_note.murmur.md --input title=test_note --input body='  hello from murmur  ' --input publish=false --json
python3 runtime/murmur.py examples/refrain_guard.murmur.md --json
