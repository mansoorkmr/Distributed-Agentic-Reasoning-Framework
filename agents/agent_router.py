"""
Distributed Agentic Reasoning Framework (DARF)

Agent Router

Purpose
-------
Determines which registered agent should handle
an incoming request.

Responsibilities
----------------
- Route by agent ID
- Route by capability
- Route default agent
- Validate routing configuration

Design Principles
-----------------
- Stateless routing
- Fast lookup (O(1) dictionary access via Registry)
- Extensible
- Production-ready

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agents.agent import Agent
from agents.agent_registry import AgentRegistry

__all__ = ["AgentRouter"]


# ============================================================
# AGENT ROUTER
# ============================================================

@dataclass(slots=True)
class AgentRouter:
    """
    Canonical DARF Agent Router.
    """

    registry: AgentRegistry
    default_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    # ========================================================
    # ROUTING
    # ========================================================

    def route(self, agent_id: str) -> Agent:
        """Route to a registered agent."""
        agent = self.registry.get(agent_id)
        if agent is None:
            raise ValueError(f"Unknown agent '{agent_id}'.")
        return agent

    def contains(self, agent_id: str) -> bool:
        """Determine whether an agent is registered."""
        return self.registry.contains(agent_id)

    # ========================================================
    # DEFAULT AGENT
    # ========================================================

    def set_default(self, agent_id: str) -> None:
        """Configure the default agent."""
        if not self.registry.contains(agent_id):
            raise ValueError(f"Unknown agent '{agent_id}'. Cannot set as default.")
        self.default_agent = agent_id

    def has_default(self) -> bool:
        """Determine whether a default agent exists."""
        return self.default_agent is not None

    def route_default(self) -> Agent:
        """Return the default agent."""
        if not self.has_default():
            raise ValueError("No default agent configured.")
        # We can safely ignore the type checker here because has_default() guarantees it's a string
        return self.route(self.default_agent)  # type: ignore

    def clear_default(self) -> None:
        """Remove the default agent."""
        self.default_agent = None

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate(self) -> None:
        """Validate router configuration."""
        if self.default_agent is not None and not self.registry.contains(self.default_agent):
            raise ValueError("Default agent is configured but not registered in the AgentRegistry.")

    # ========================================================
    # DISCOVERY
    # ========================================================

    def available_agents(self) -> List[str]:
        """Return the IDs of all registered agents."""
        return self.registry.names()

    def agents(self) -> List[Agent]:
        """Return all registered agents."""
        return self.registry.values()

    def count(self) -> int:
        """Return the number of registered agents."""
        return self.registry.count()

    def is_empty(self) -> bool:
        """Determine whether no agents are registered."""
        return self.registry.is_empty()

    # ========================================================
    # INFORMATION
    # ========================================================

    def default(self) -> Optional[str]:
        """Return the configured default agent ID."""
        return self.default_agent

    def supports(self, agent_id: str) -> bool:
        """Determine whether the router can route to the specified agent."""
        return self.contains(agent_id)

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the router state."""
        return {
            "agent_count": self.count(),
            "agents": self.available_agents(),
            "default_agent": self.default_agent,
            "has_default": self.has_default(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """Serialize the router to a JSON string."""
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __len__(self) -> int:
        """Return the number of registered agents."""
        return self.count()

    def __contains__(self, agent_id: str) -> bool:
        """Determine whether the specified agent is registered."""
        return self.contains(agent_id)

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"AgentRouter({self.count()} agents)"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"<AgentRouter agents={self.count()} default={self.default_agent!r}>"