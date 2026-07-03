"""
Distributed Agentic Reasoning Framework (DARF)

Memory Agent

Purpose
-------
Provides the canonical memory agent for DARF.

Responsibilities
----------------
- Read memory
- Write memory
- Update memory
- Remove memory
- Bridge Agent Layer with Memory subsystem
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_context import AgentContext

# CORRECTED IMPORT PATH based on your DARF Runtime architecture
from memory.manager.memory_manager import MemoryManager

__all__ = ["MemoryAgent"]


# ============================================================
# MEMORY AGENT
# ============================================================

@dataclass(slots=True)
class MemoryAgent(BaseAgent):
    """
    Canonical DARF Memory Agent.
    Serves as the bridge between the Agent routing layer and the Memory subsystem.
    """

    id: str = "memory"
    name: str = "Memory Agent"
    description: str = "Reads and writes DARF memory."
    version: str = "1.0"

    memory: MemoryManager = field(default_factory=MemoryManager)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ========================================================
    # EXECUTION
    # ========================================================

    def run(self, context: AgentContext, **kwargs: Any) -> Any:
        """
        Execute a memory operation (read, write, delete).
        """
        operation = kwargs.get("operation", "read")
        key = kwargs.get("key")
        value = kwargs.get("value")

        if key is None:
            raise ValueError("Memory key is required.")

        if operation == "read":
            result = self.memory.recall(key) if hasattr(self.memory, 'recall') else self.memory.get(key)

        elif operation == "write":
            if hasattr(self.memory, 'remember'):
                self.memory.remember(key, value)
            else:
                self.memory.set(key, value)
            result = value

        elif operation == "delete":
            if hasattr(self.memory, 'forget'):
                self.memory.forget(key)
            else:
                self.memory.remove(key)
            result = None

        else:
            raise ValueError(f"Unsupported memory operation '{operation}'.")

        context.set_output(self.agent_id, result)
        return result

    # ========================================================
    # MEMORY UTILITIES
    # ========================================================

    def memory_ready(self) -> bool:
        return self.memory is not None

    def reset(self) -> None:
        if hasattr(self.memory, "clear"):
            self.memory.clear()
        elif hasattr(self.memory, "reset"):
            self.memory.reset()
        self.metadata.clear()

    def get_capabilities(self) -> List[str]:
        return [
            "memory_read",
            "memory_write",
            "memory_delete",
            "memory_storage",
        ]

    def supports(self, capability: str) -> bool:
        return capability in self.get_capabilities()

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "memory_ready": self.memory_ready(),
            "supported_capabilities": self.get_capabilities(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    def __str__(self) -> str:
        return f"MemoryAgent(ready={self.memory_ready()})"

    def __repr__(self) -> str:
        return f"<MemoryAgent id='{self.agent_id}' ready={self.memory_ready()}>"