from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MurmurIntegrationRequest:
    surface: str
    action: str
    args: dict[str, Any]


@dataclass(frozen=True)
class MurmurIntegrationResult:
    surface: str
    action: str
    ok: bool
    data: Any = None
    error: str | None = None


class MurmurIntegrationRegistry:
    def __init__(self, adapters: dict[str, Any] | None = None) -> None:
        self._adapters = adapters or {}

    def register(self, surface: str, adapter: Any) -> None:
        self._adapters[surface] = adapter

    def surfaces(self) -> list[str]:
        return sorted(self._adapters.keys())

    def invoke(self, request: MurmurIntegrationRequest) -> MurmurIntegrationResult:
        adapter = self._adapters.get(request.surface)
        if adapter is None:
            return MurmurIntegrationResult(
                surface=request.surface,
                action=request.action,
                ok=False,
                error=f"Unknown integration surface: {request.surface}",
            )

        handler = getattr(adapter, request.action, None)
        if handler is None or not callable(handler):
            return MurmurIntegrationResult(
                surface=request.surface,
                action=request.action,
                ok=False,
                error=f"Unsupported action for {request.surface}: {request.action}",
            )

        data = handler(**request.args)
        return MurmurIntegrationResult(
            surface=request.surface,
            action=request.action,
            ok=True,
            data=data,
        )


class LoopAdapter:
    def status(self) -> dict[str, Any]:
        return {"kind": "loop", "status": "stub", "message": "Loop adapter not wired yet"}


class SettingsAdapter:
    def status(self) -> dict[str, Any]:
        return {"kind": "settings", "status": "stub", "message": "Settings adapter not wired yet"}


class CalendarAdapter:
    def status(self) -> dict[str, Any]:
        return {"kind": "calendar", "status": "stub", "message": "Calendar adapter not wired yet"}


def build_default_registry() -> MurmurIntegrationRegistry:
    registry = MurmurIntegrationRegistry()
    registry.register("loop", LoopAdapter())
    registry.register("settings", SettingsAdapter())
    registry.register("calendar", CalendarAdapter())
    return registry
