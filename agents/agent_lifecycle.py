"""
Distributed Agentic Reasoning Framework (DARF)
Agent Runtime

Agent Lifecycle

Purpose
-------
Defines the runtime lifecycle of DARF agents.

Responsibilities
----------------
- Lifecycle state
- State transitions
- State queries
- Serialization

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from enum import Enum

from typing import Any
from typing import Dict

__all__ = [
    "AgentLifecycleState",
    "AgentLifecycle",
]
# ============================================================
# AGENT LIFECYCLE STATE
# ============================================================


class AgentLifecycleState(
    str,
    Enum,
):
    CREATED = "created"

    INITIALIZED = "initialized"

    READY = "ready"

    RUNNING = "running"

    IDLE = "idle"

    STOPPED = "stopped"

    FAILED = "failed"
    # ============================================================
# AGENT LIFECYCLE
# ============================================================


@dataclass(slots=True)
class AgentLifecycle:
    """
    Runtime lifecycle controller.
    """

    state: AgentLifecycleState = (
        AgentLifecycleState.CREATED
    )

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
        # ========================================================
    # TRANSITIONS
    # ========================================================

    def initialize(
        self,
    ) -> None:

        self.state = (
            AgentLifecycleState.INITIALIZED
        )

    def ready(
        self,
    ) -> None:

        self.state = (
            AgentLifecycleState.READY
        )

    def run(
        self,
    ) -> None:

        self.state = (
            AgentLifecycleState.RUNNING
        )

    def idle(
        self,
    ) -> None:

        self.state = (
            AgentLifecycleState.IDLE
        )

    def stop(
        self,
    ) -> None:

        self.state = (
            AgentLifecycleState.STOPPED
        )

    def fail(
        self,
    ) -> None:

        self.state = (
            AgentLifecycleState.FAILED
        )
            # ========================================================
    # HELPERS
    # ========================================================

    def is_running(
        self,
    ) -> bool:

        return (
            self.state
            is AgentLifecycleState.RUNNING
        )

    def is_ready(
        self,
    ) -> bool:

        return (
            self.state
            is AgentLifecycleState.READY
        )

    def is_failed(
        self,
    ) -> bool:

        return (
            self.state
            is AgentLifecycleState.FAILED
        )
        # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[
        str,
        Any,
    ]:

        return {

            "state": self.state.value,

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(
        self,
    ) -> str:

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )
        # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(
        self,
    ) -> str:

        return (
            f"Lifecycle("
            f"{self.state.value})"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<AgentLifecycle "
            f"state='{self.state.value}'>"
        )