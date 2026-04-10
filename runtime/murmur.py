#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from integrations import (
    MurmurIntegrationRequest,
    build_default_registry,
)

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
    skipped: bool = False


class MurmurRuntime:
    def __init__(self, document: dict[str, Any], inputs: dict[str, Any] | None = None) -> None:
        self.document = document
        self.inputs = inputs or {}
        self.variables: dict[str, Any] = {}
        self.steps: dict[str, StepResult] = {}
        self.outputs: list[Any] = []
        self.witnesses: list[dict[str, Any]] = []
        self.stopped = False
        self.integrations = build_default_registry()

    def run(self) -> dict[str, Any]:
        for block in self.document.get("blocks", []):
            if self.stopped:
                break
            if isinstance(block, dict) and "steps" in block:
                self._run_steps(block["steps"])
        return {
            "inputs": self.inputs,
            "variables": self.variables,
            "steps": {name: result.output for name, result in self.steps.items()},
            "outputs": self.outputs,
            "witnesses": self.witnesses,
            "stopped": self.stopped,
        }

    def _run_steps(self, steps: list[dict[str, Any]]) -> None:
        for index, step in enumerate(steps, start=1):
            if self.stopped:
                break
            if not isinstance(step, dict):
                raise TypeError(f"Step {index} must be a mapping")

            step_id_template = step.get("id") or step.get("name") or f"step_{index}"
            step_id = self.resolve(step_id_template) if isinstance(step_id_template, str) else step_id_template
            when = step.get("when")
            if when is not None and not self._is_truthy(self.resolve(when)):
                self.steps[step_id] = StepResult(id=step_id, skipped=True, data={"when": self.resolve(when)})
                continue

            primitive_name, primitive_payload = self._extract_primitive(step)
            resolved_payload = self._resolve_payload(primitive_name, primitive_payload)
            output = self._execute_primitive(primitive_name, resolved_payload)
            self.steps[step_id] = StepResult(id=step_id, output=output, data=resolved_payload)

            into = resolved_payload.get("into") if isinstance(resolved_payload, dict) else None
            if into:
                self.variables[into] = output

    def _extract_primitive(self, step: dict[str, Any]) -> tuple[str, Any]:
        reserved = {"id", "name", "when", "note", "timeout", "on_error", "tags"}
        candidates = [(key, value) for key, value in step.items() if key not in reserved]
        if len(candidates) != 1:
            raise ValueError(f"Each step must declare exactly one primitive, got {list(step.keys())}")
        return candidates[0]

    def _execute_primitive(self, primitive: str, payload: Any) -> Any:
        handler = getattr(self, f"primitive_{primitive}", None)
        if handler is None:
            raise ValueError(f"Unknown primitive: {primitive}")
        return handler(payload)

    def _resolve_payload(self, primitive: str, payload: Any) -> Any:
        if primitive == "repeat" and isinstance(payload, dict):
            resolved = {
                key: value if key == "steps" else self.resolve(value)
                for key, value in payload.items()
            }
            return resolved
        return self.resolve(payload)

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
        value = payload.get("value", payload.get("from"))
        mode = payload.get("mode", payload.get("rule", "strip"))
        if isinstance(value, str):
            if mode in {"strip", "trim"}:
                return value.strip()
            if mode == "lines":
                return [line.strip() for line in value.splitlines() if line.strip()]
            if mode in {"lower", "lowercase"}:
                return value.lower().strip()
            if mode == "slugify":
                slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
                return slug
        if mode == "keys" and isinstance(value, dict):
            return list(value.keys())
        return value

    def primitive_heed(self, payload: dict[str, Any]) -> Any:
        source = payload.get("from", "input")
        required = bool(payload.get("required", False))

        if source == "input":
            key = payload.get("key")
            value = self.inputs.get(key)
        elif source == "env":
            key = payload.get("key")
            value = os.environ.get(str(key)) if key is not None else None
        elif source == "file":
            path_value = payload.get("path")
            if not path_value:
                raise ValueError("heed.path is required when from=file")
            value = Path(path_value).read_text(encoding="utf-8")
        elif source == "state":
            key = payload.get("key")
            value = self.variables.get(str(key)) if key is not None else None
        else:
            raise ValueError(f"Unsupported heed.from source: {source}")

        if required and value is None:
            locator = payload.get("key") or payload.get("path") or "<unknown>"
            raise ValueError(f"Required heed source missing: {source}:{locator}")
        return value

    def primitive_choose(self, payload: dict[str, Any]) -> Any:
        options = payload.get("from", [])
        if not isinstance(options, list):
            raise TypeError("choose.from must be a list")

        for option in options:
            if not isinstance(option, dict):
                raise TypeError("choose options must be mappings")
            if self._is_truthy(option.get("when", True)):
                return option.get("value")
        return payload.get("default")

    def primitive_repeat(self, payload: dict[str, Any]) -> list[Any]:
        steps = payload.get("steps")
        if not isinstance(steps, list):
            raise ValueError("repeat.steps must be a list")

        if "for_each" in payload:
            items = payload.get("for_each")
            if not isinstance(items, list):
                raise TypeError("repeat.for_each must resolve to a list")
        else:
            times = int(payload.get("times", 0))
            items = list(range(times))

        loop_var = payload.get("as", "item")
        index_var = payload.get("index_as")
        previous_loop = self.variables.get(loop_var)
        previous_index = self.variables.get(index_var) if index_var else None
        had_previous_loop = loop_var in self.variables
        had_previous_index = index_var in self.variables if index_var else False

        results: list[Any] = []
        for index, item in enumerate(items):
            self.variables[loop_var] = item
            if index_var:
                self.variables[index_var] = index
            before = set(self.steps)
            self._run_steps(steps)
            new_step_ids = [step_id for step_id in self.steps if step_id not in before]
            if new_step_ids:
                results.append(self.steps[new_step_ids[-1]].output)
            else:
                results.append(None)
            if self.stopped:
                break

        if had_previous_loop:
            self.variables[loop_var] = previous_loop
        else:
            self.variables.pop(loop_var, None)
        if index_var:
            if had_previous_index:
                self.variables[index_var] = previous_index
            else:
                self.variables.pop(index_var, None)
        return results

    def primitive_witness(self, payload: dict[str, Any]) -> Any:
        record = {
            "label": payload.get("label"),
            "value": payload.get("value"),
            "to": payload.get("to", "trace"),
        }
        self.witnesses.append(record)
        if record["to"] == "stdout":
            print(f"[witness] {record['label']}: {record['value']}")
        elif record["to"] == "file":
            path_value = payload.get("path")
            if not path_value:
                raise ValueError("witness.path is required when to=file")
            path = Path(path_value)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record["value"]

    def primitive_store(self, payload: dict[str, Any]) -> Any:
        value = payload.get("value")
        destination = payload.get("to", "state")
        mode = payload.get("mode", "overwrite")

        if destination == "state":
            key = payload.get("key") or payload.get("into")
            if not key:
                raise ValueError("store.key or store.into is required when to=state")
            self.variables[str(key)] = value
            return value

        if destination == "file":
            path_value = payload.get("path")
            if not path_value:
                raise ValueError("store.path is required when to=file")
            path = Path(path_value)
            path.parent.mkdir(parents=True, exist_ok=True)
            content = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False)
            if mode == "append":
                with path.open("a", encoding="utf-8") as handle:
                    handle.write(str(content))
                    if isinstance(content, str) and not content.endswith("\n"):
                        handle.write("\n")
            else:
                path.write_text(str(content), encoding="utf-8")
            return str(path)

        raise ValueError(f"Unsupported store.to destination: {destination}")

    def primitive_refrain(self, payload: dict[str, Any]) -> Any:
        mode = payload.get("mode", "skip")
        reason = payload.get("reason")
        if mode in {"halt", "stop"}:
            self.stopped = True
        return {"mode": mode, "reason": reason}

    def primitive_invoke(self, payload: dict[str, Any]) -> Any:
        surface = payload.get("tool")
        action = payload.get("action", "status")
        args = payload.get("with", {})
        if not surface:
            raise ValueError("invoke.tool is required")
        if not isinstance(args, dict):
            raise TypeError("invoke.with must be a mapping")

        result = self.integrations.invoke(
            MurmurIntegrationRequest(surface=str(surface), action=str(action), args=args)
        )
        if not result.ok:
            raise ValueError(result.error or f"Integration invoke failed: {surface}.{action}")
        return result.data

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
        elif root == "meta":
            current = self.document.get("frontmatter", {})
            parts = parts[1:]
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

    def _is_truthy(self, value: Any) -> bool:
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"", "0", "false", "no", "off", "null", "none"}:
                return False
            return True
        return bool(value)


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


def parse_inputs(raw_inputs: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for item in raw_inputs:
        if "=" not in item:
            raise ValueError(f"Inputs must use key=value form, got: {item}")
        key, value = item.split("=", 1)
        parsed[key] = yaml.safe_load(value)
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
