"""
Distributed Agentic Reasoning Framework (DARF)
Agent Runtime

Agent Policy

Purpose
-------
Defines the canonical runtime policy used by DARF
agents.

Responsibilities
----------------
- Timeout policy
- Retry policy
- Concurrency policy
- Permission policy
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
    "AgentPolicy",
]
# ============================================================
# AGENT POLICY
# ============================================================


@dataclass(slots=True)
class AgentPolicy:
    """
    Canonical runtime policy.
    """

    timeout_seconds: float = 300.0

    max_retries: int = 3

    allow_parallel_execution: bool = True

    allow_tool_usage: bool = True

    allow_memory_access: bool = True

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

        if self.timeout_seconds <= 0:

            raise ValueError(
                "timeout_seconds must be > 0."
            )

        if self.max_retries < 0:

            raise ValueError(
                "max_retries must be >= 0."
            )
            # ========================================================
    # HELPERS
    # ========================================================

    def tool_usage_enabled(
        self,
    ) -> bool:

        return self.allow_tool_usage

    def memory_access_enabled(
        self,
    ) -> bool:

        return self.allow_memory_access

    def parallel_execution_enabled(
        self,
    ) -> bool:

        return self.allow_parallel_execution
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
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "allow_parallel_execution":
                self.allow_parallel_execution,
            "allow_tool_usage":
                self.allow_tool_usage,
            "allow_memory_access":
                self.allow_memory_access,
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
            f"AgentPolicy("
            f"timeout={self.timeout_seconds}s)"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<AgentPolicy "
            f"timeout={self.timeout_seconds}s "
            f"retries={self.max_retries}>"
        )
    