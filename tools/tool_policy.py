"""
Distributed Agentic Reasoning Framework (DARF)

Tool Policy
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class ToolPolicy:

    timeout_seconds: float = 60.0

    max_retries: int = 3

    allow_parallel_execution: bool = True

    allow_external_tools: bool = True

    require_approval: bool = False

    sandbox_enabled: bool = True

    metadata: dict = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------

    def parallel_enabled(self) -> bool:

        return self.allow_parallel_execution

    def external_tools_enabled(self) -> bool:

        return self.allow_external_tools

    def approval_required(self) -> bool:

        return self.require_approval

    def sandbox_active(self) -> bool:

        return self.sandbox_enabled

    def retries_allowed(self) -> bool:

        return self.max_retries > 0

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "timeout_seconds": self.timeout_seconds,

            "max_retries": self.max_retries,

            "allow_parallel_execution": self.allow_parallel_execution,

            "allow_external_tools": self.allow_external_tools,

            "require_approval": self.require_approval,

            "sandbox_enabled": self.sandbox_enabled,

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(self):

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(self):

        return (

            f"ToolPolicy(timeout={self.timeout_seconds}s)"

        )

    def __repr__(self):

        return (

            "<ToolPolicy "

            f"timeout={self.timeout_seconds}s "

            f"retries={self.max_retries}>"

        )