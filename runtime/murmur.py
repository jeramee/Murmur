#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to run Murmur prototype runtime") from exc

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
FENCED_YAML_RE = re.compile(r"```yaml\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)
TEMPLATE_RE = re.compile(r"\$\{([^}]+)\}")


@dataclass
class StepResult:
    id: str
    output: Any = None
    data: dict[str, Any] | None = None


class MurmurRuntime:
    def __init__(self, document: dict[str, Any], inputs: dict[str, Any] | None = None) -> None:
        self.document = document
        self.inputs = inputs or {}
        self.variables: dict[str, Any] = {}
        self.steps: dict[str, StepResult] = {}
        self.outputs: list[Any] = []

    def run(self) -> dict[str, Any]:
        for block in self.document.get("blocks", []):
            if isinstance(block, dict) and "steps" in block:
                self._run_steps(block["steps"])
        return {
            "inputs": self.inputs,
            "variables": self.variables,
            "steps": {name: result.output for name, result in self.steps.items()},
            "outputs": self.outputs,
        }

    def _run_steps(self, steps: list[dict[str, Any]]) -> None:
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                raise TypeError(f"Step {index} must be a mapping")

            step_id = step.get("id") or step.get("name") or f"step_{index}"
            primitive_name, primitive_payload = self._extract_primitive(step)
            resolved_payload = self.resolve(primitive_payload)
            output = self._execute_primitive(primitive_name, resolved_payload)
            self.steps[step_id] = StepResult(id=step_id, output=output, data=resolved_payload)

            into = resolved_payload.get("into") if isinstance(resolved_payload, dict) else None
            if into:
                self.variables[into] = output

    def _extract_primitive(self, step: dict[str, Any]) -> tuple[str, Any]:
        reserved = {"id", "name", "when", "note"}
        candidates = [(key, value) for key, value in step.items() if key not in reserved]
        if len(candidates) != 1:
            raise ValueError(f"Each step must declare exactly one primitive, got {list(step.keys())}")
        return candidates[0]

    def _execute_primitive(self, primitive: str, payload: Any) -> Any:
        handler = getattr(self, f"primitive_{primitive}", None)
        if handler is None:
            raise ValueError(f"Unknown primitive: {primitive}")
        return handler(payload)

    def primitive_weave(self, payload: dict[str, Any]) -> str:
        pattern = str(payload.get("pattern", ""))
        context = payload.get("with", {})
        if not isinstance(context, dict):
            raise TypeError("weave.with must be a mapping")
        return pattern.format(**context)

    def primitive_utter(self, payload: dict[str, Any]) -> Any:
        value = payload.get("value")
        print(value)
        self.outputs.append(value)
        return value

    def primitive_write(self, payload: dict[str, Any]) -> str:
        path_value = payload.get("path")
        if not path_value:
            raise ValueError("write.path is required")
        path = Path(path_value)
        path.parent.mkdir(parents=True, exist_ok=True)
        content = payload.get("content", "")
        path.write_text(str(content), encoding="utf-8")
        return str(path)

    def primitive_distill(self, payload: dict[str, Any]) -> Any:
        value = payload.get("value")
        mode = payload.get("mode", "strip")
        if isinstance(value, str):
            if mode == "strip":
                return value.strip()
            if mode == "lines":
                return [line.strip() for line in value.splitlines() if line.strip()]
            if mode == "lower":
                return value.lower().strip()
        if mode == "keys" and isinstance(value, dict):
            return list(value.keys())
        return value

    def resolve(self, value: Any) -> Any:
        if isinstance(value, str):
            return self._resolve_string(value)
        if isinstance(value, list):
            return [self.resolve(item) for item in value]
        if isinstance(value, dict):
            return {key: self.resolve(item) for key, item in value.items()}
        return value

    def _resolve_string(self, template: str) -> Any:
        match = TEMPLATE_RE.fullmatch(template)
        if match:
            return self._lookup(match.group(1).strip())

        def replace(m: re.Match[str]) -> str:
            looked_up = self._lookup(m.group(1).strip())
            if isinstance(looked_up, (dict, list)):
                return json.dumps(looked_up)
            return "" if looked_up is None else str(looked_up)

        return TEMPLATE_RE.sub(replace, template)

    def _lookup(self, expression: str) -> Any:
        parts = expression.split(".")
        if not parts:
            return None

        root = parts[0]
        if root == "inputs":
            current: Any = self.inputs
            parts = parts[1:]
        elif root == "steps":
            if len(parts) < 3 or parts[2] != "output":
                raise ValueError(f"Unsupported step reference: ${{{expression}}}")
            step = self.steps.get(parts[1])
            if step is None:
                raise KeyError(f"Unknown step id: {parts[1]}")
            current = step.output
            parts = parts[3:]
        else:
            current = self.variables.get(root)
            parts = parts[1:]

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                current = current[int(part)]
            else:
                return None
        return current


def load_document(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    frontmatter = {}
    frontmatter_match = FRONTMATTER_RE.match(text)
    if frontmatter_match:
        frontmatter = yaml.safe_load(frontmatter_match.group(1)) or {}

    blocks = []
    for match in FENCED_YAML_RE.finditer(text):
        data = yaml.safe_load(match.group(1))
        if data is not None:
            blocks.append(data)

    return {
        "path": str(path),
        "frontmatter": frontmatter,
        "blocks": blocks,
    }


def parse_inputs(raw_inputs: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in raw_inputs:
        if "=" not in item:
            raise ValueError(f"Inputs must use key=value form, got: {item}")
        key, value = item.split("=", 1)
        parsed[key] = value
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a Murmur markdown workflow")
    parser.add_argument("document", help="Path to .murmur.md file")
    parser.add_argument("--input", action="append", default=[], help="Input value in key=value form")
    parser.add_argument("--json", action="store_true", help="Emit final runtime state as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    document = load_document(Path(args.document))
    runtime = MurmurRuntime(document=document, inputs=parse_inputs(args.input))
    result = runtime.run()

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
