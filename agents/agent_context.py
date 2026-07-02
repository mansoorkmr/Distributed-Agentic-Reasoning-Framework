"""
Distributed Agentic Reasoning Framework (DARF)
Agent Runtime

Agent Context

Purpose
-------
Defines the canonical execution context shared between
DARF agents.

Responsibilities
----------------
- Shared execution state
- Request context
- Metadata storage
- Variable storage
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
from typing import Optional

__all__ = [
    "AgentContext",
]
# ============================================================
# AGENT CONTEXT
# ============================================================


@dataclass(slots=True)
class AgentContext:
    """
    Canonical execution context.
    """

    request_id: Optional[str] = None

    execution_id: Optional[str] = None

    session_id: Optional[str] = None

    variables: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
        # ========================================================
    # VARIABLES
    # ========================================================

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.variables[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.variables.get(
            key,
            default,
        )

    def contains(
        self,
        key: str,
    ) -> bool:

        return (
            key
            in self.variables
        )

    def remove(
        self,
        key: str,
    ) -> None:

        self.variables.pop(
            key,
            None,
        )

    def clear(
        self,
    ) -> None:

        self.variables.clear()
            # ========================================================
    # HELPERS
    # ========================================================

    def variable_count(
        self,
    ) -> int:

        return len(
            self.variables
        )

    def is_empty(
        self,
    ) -> bool:

        return (
            self.variable_count()
            == 0
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
            "request_id": self.request_id,
            "execution_id": self.execution_id,
            "session_id": self.session_id,
            "variables": self.variables,
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
            default=str,
        )
        # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(
        self,
    ) -> str:

        return (
            f"AgentContext("
            f"{self.variable_count()} variables)"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<AgentContext "
            f"variables={self.variable_count()}>"
        )
    