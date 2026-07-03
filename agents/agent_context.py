"""
Distributed Agentic Reasoning Framework (DARF)

Agent Context

Purpose
-------
Defines the canonical execution context shared by
every DARF agent.

Responsibilities
----------------
- Store global execution state (IDs, Current Agent)
- Store shared variables
- Store agent-specific outputs
- Manage metadata and lifecycle

Design Principles
-----------------
- Lightweight and thread-safe
- Fully serializable
- Mutable execution state for runtime updates
- Production-ready
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

__all__ = ["AgentContext"]

# ============================================================
# AGENT CONTEXT
# ============================================================

@dataclass(slots=True)
class AgentContext:
    """
    Canonical agent execution context.
    """

    request_id: Optional[str] = None
    session_id: Optional[str] = None
    execution_id: Optional[str] = None
    current_agent: Optional[str] = None

    variables: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    version: str = "1.0"

    # ========================================================
    # VARIABLES (Shared State)
    # ========================================================

    def set(self, key: str, value: Any) -> None:
        self.variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)

    def contains(self, key: str) -> bool:
        return key in self.variables

    # ========================================================
    # OUTPUTS (Inter-Agent Communication)
    # ========================================================

    def set_output(self, agent: str, output: Any) -> None:
        """Stores the result of a specific agent's execution."""
        self.outputs[agent] = output

    def output(self, agent: str) -> Any:
        """Retrieves the stored result of a specific agent."""
        return self.outputs.get(agent)

    # ========================================================
    # UTILITIES
    # ========================================================

    def clear(self) -> None:
        """Resets the context for a new execution lifecycle."""
        self.variables.clear()
        self.outputs.clear()
        self.metadata.clear()
        self.current_agent = None

    def is_empty(self) -> bool:
        return not self.variables and not self.outputs

    def variable_count(self) -> int:
        return len(self.variables)

    def output_count(self) -> int:
        return len(self.outputs)

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize context to dictionary for storage/logs."""
        return {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "execution_id": self.execution_id,
            "current_agent": self.current_agent,
            "variables": self.variables,
            "outputs": self.outputs,
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """Serialize context to JSON string."""
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(self) -> str:
        return f"AgentContext({self.variable_count()} vars, {self.output_count()} outputs)"

    def __repr__(self) -> str:
        return (
            f"<AgentContext "
            f"agent='{self.current_agent}' "
            f"vars={self.variable_count()} "
            f"outputs={self.output_count()}>"
        )