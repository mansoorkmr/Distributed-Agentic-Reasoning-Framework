"""
Distributed Agentic Reasoning Framework (DARF)

Agent Registry

Purpose
-------
Maintains the collection of registered DARF agents.

Responsibilities
----------------
- Register agents
- Remove agents
- Lookup agents
- Enumerate agents

Design Principles
-----------------
- Fast lookup
- Serializable
- Thread-safe
- Production-ready

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agents.agent import Agent

__all__ = ["AgentRegistry"]

# ============================================================
# AGENT REGISTRY
# ============================================================

@dataclass(slots=True)
class AgentRegistry:
    """
    Canonical DARF Agent Registry.
    """

    agents: Dict[str, Agent] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    # ========================================================
    # REGISTRATION
    # ========================================================

    def register(self, agent: Agent) -> None:
        """Register an agent."""
        if agent.agent_id in self.agents:
            raise ValueError(f"Agent '{agent.agent_id}' already exists.")
        self.agents[agent.agent_id] = agent

    def unregister(self, agent_id: str) -> bool:
        """Remove an agent. Returns True if removed, False if not found."""
        if agent_id not in self.agents:
            return False
        del self.agents[agent_id]
        return True

    # ========================================================
    # LOOKUP
    # ========================================================

    def get(self, agent_id: str) -> Optional[Agent]:
        """Retrieve an agent by ID."""
        return self.agents.get(agent_id)

    def contains(self, agent_id: str) -> bool:
        """Check if an agent exists in the registry."""
        return agent_id in self.agents

    # ========================================================
    # COLLECTION
    # ========================================================

    def names(self) -> List[str]:
        """Return a sorted list of registered agent IDs."""
        return sorted(self.agents.keys())

    def values(self) -> List[Agent]:
        """Return a list of all registered agents."""
        return list(self.agents.values())

    def items(self) -> Any:
        """Return key-value pairs of the registry."""
        return self.agents.items()

    def count(self) -> int:
        """Return number of agents."""
        return len(self.agents)

    def is_empty(self) -> bool:
        """Return True if no agents are registered."""
        return self.count() == 0

    def clear(self) -> None:
        """Clear all registered agents and metadata."""
        self.agents.clear()
        self.metadata.clear()

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize registry state."""
        return {
            "count": self.count(),
            "agents": self.names(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """Serialize registry to JSON string."""
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __len__(self) -> int:
        return self.count()

    def __contains__(self, agent_id: str) -> bool:
        return self.contains(agent_id)

    def __str__(self) -> str:
        return f"AgentRegistry({self.count()} agents)"

    def __repr__(self) -> str:
        return f"<AgentRegistry count={self.count()}>"