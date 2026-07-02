"""
Distributed Agentic Reasoning Framework (DARF)
Agent Runtime

Agent Capability

Purpose
-------
Defines the canonical capability description used by
DARF agents.

Responsibilities
----------------
- Capability declaration
- Capability matching
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

from typing import Any
from typing import Dict

__all__ = [
    "AgentCapability",
]
# ============================================================
# AGENT CAPABILITY
# ============================================================


@dataclass(slots=True)
class AgentCapability:
    """
    Canonical agent capability.
    """

    name: str

    description: str = ""

    enabled: bool = True

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"

    def __post_init__(
        self,
    ) -> None:

        if not self.name.strip():

            raise ValueError(
                "Capability name cannot be empty."
            )
            # ========================================================
    # HELPERS
    # ========================================================

    def enable(
        self,
    ) -> None:

        self.enabled = True

    def disable(
        self,
    ) -> None:

        self.enabled = False

    def is_enabled(
        self,
    ) -> bool:

        return self.enabled

    def matches(
        self,
        name: str,
    ) -> bool:

        return (
            self.name.lower()
            == name.lower()
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
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
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

        state = (
            "enabled"
            if self.enabled
            else "disabled"
        )

        return (
            f"{self.name} ({state})"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<AgentCapability "
            f"name='{self.name}' "
            f"enabled={self.enabled}>"
        )