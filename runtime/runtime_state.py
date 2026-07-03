"""
Distributed Agentic Reasoning Framework (DARF) - Runtime State

Represents the lifecycle state of the DARF runtime.
"""

from __future__ import annotations

import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict


class RuntimeStatus(str, Enum):
    """Enumeration of possible runtime lifecycle states."""
    CREATED = "created"
    INITIALIZED = "initialized"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(slots=True)
class RuntimeState:
    status: RuntimeStatus = RuntimeStatus.CREATED
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    # ---------------------------------------------------------
    # State Transitions
    # ---------------------------------------------------------

    def initialize(self) -> None:
        self.status = RuntimeStatus.INITIALIZED

    def ready(self) -> None:
        self.status = RuntimeStatus.READY

    def run(self) -> None:
        self.status = RuntimeStatus.RUNNING

    def pause(self) -> None:
        self.status = RuntimeStatus.PAUSED

    def stop(self) -> None:
        self.status = RuntimeStatus.STOPPED

    def fail(self) -> None:
        self.status = RuntimeStatus.FAILED

    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------

    def is_ready(self) -> bool:
        return self.status == RuntimeStatus.READY

    def is_running(self) -> bool:
        return self.status == RuntimeStatus.RUNNING

    def is_paused(self) -> bool:
        return self.status == RuntimeStatus.PAUSED

    def is_failed(self) -> bool:
        return self.status == RuntimeStatus.FAILED

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(self) -> str:
        return f"RuntimeState({self.status.value})"

    def __repr__(self) -> str:
        return f"<RuntimeState status='{self.status.value}'>"