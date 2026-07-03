"""
Distributed Agentic Reasoning Framework (DARF) - Runtime Context

Stores shared runtime objects and variables.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, TYPE_CHECKING

# Prevent circular imports while maintaining strict type hinting
if TYPE_CHECKING:
    from planner.planner import Planner
    from execution.execution_engine import ExecutionEngine
    from memory.manager.memory_manager import MemoryManager
    from agents.agent_registry import AgentRegistry
    from communication.message_bus import MessageBus


@dataclass(slots=True)
class RuntimeContext:
    request_id: Optional[str] = None
    session_id: Optional[str] = None

    # Core Subsystems
    planner: Optional['Planner'] = None
    execution_engine: Optional['ExecutionEngine'] = None
    memory_manager: Optional['MemoryManager'] = None
    agent_registry: Optional['AgentRegistry'] = None
    message_bus: Optional['MessageBus'] = None

    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    # ---------------------------------------------------------
    # Variable Management
    # ---------------------------------------------------------

    def set(self, key: str, value: Any) -> None:
        """Sets a variable in the runtime context."""
        self.variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a variable, returning a default if not found."""
        return self.variables.get(key, default)

    def remove(self, key: str) -> None:
        """Removes a variable from the context."""
        self.variables.pop(key, None)

    def contains(self, key: str) -> bool:
        """Checks if a variable exists in the context."""
        return key in self.variables

    def clear(self) -> None:
        """Clears all variables."""
        self.variables.clear()

    def variable_count(self) -> int:
        """Returns the number of stored variables."""
        return len(self.variables)

    def is_empty(self) -> bool:
        """Returns True if there are no stored variables."""
        return self.variable_count() == 0

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the context to a dictionary."""
        return {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "planner": None if self.planner is None else str(self.planner),
            "execution_engine": None if self.execution_engine is None else str(self.execution_engine),
            "memory_manager": None if self.memory_manager is None else str(self.memory_manager),
            "agent_registry": None if self.agent_registry is None else str(self.agent_registry),
            "message_bus": None if self.message_bus is None else str(self.message_bus),
            "variables": {k: str(v) for k, v in self.variables.items()},
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """Serializes the context to a JSON string."""
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(self) -> str:
        return f"RuntimeContext({self.variable_count()} variables)"

    def __repr__(self) -> str:
        return f"<RuntimeContext variables={self.variable_count()}>"