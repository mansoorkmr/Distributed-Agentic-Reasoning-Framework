"""
Distributed Agentic Reasoning Framework (DARF)

Coordinator Agent

Purpose
-------
Coordinates multiple agents to accomplish complex objectives.

Responsibilities
----------------
- Delegate work to specific agents
- Execute sequences of agents
- Aggregate execution results
- Maintain global context during multi-agent workflows

Design Principles
-----------------
- Delegation over execution
- Stateless coordination
- Shared AgentContext
- Production-ready observability

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
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_context import AgentContext
from agents.agent_manager import AgentManager
from agents.agent_result import AgentResult

__all__ = ["CoordinatorAgent"]

# ============================================================
# COORDINATOR AGENT
# ============================================================

@dataclass(slots=True)
class CoordinatorAgent(BaseAgent):
    """
    Canonical DARF Coordinator Agent.
    Manages and delegates execution to a pool of registered agents.
    """

    # Override BaseAgent defaults natively to maintain perfect dataclass inheritance
    id: str = "coordinator"
    name: str = "Coordinator Agent"
    description: str = "Coordinates multiple DARF agents."
    version: str = "1.0"

    manager: AgentManager = field(default_factory=AgentManager)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ========================================================
    # AGENT MANAGEMENT
    # ========================================================

    def register_agent(self, agent: BaseAgent) -> None:
        """Register a managed agent."""
        self.manager.register(agent)

    def unregister_agent(self, agent_id: str) -> bool:
        """Remove a managed agent."""
        return self.manager.unregister(agent_id)

    # ========================================================
    # COORDINATION & EXECUTION
    # ========================================================

    def coordinate(self, agent_id: str, context: AgentContext, **kwargs: Any) -> AgentResult:
        """Execute a single managed agent by its ID."""
        return self.manager.execute_by_id(agent_id, **kwargs)

    def run(self, context: AgentContext, **kwargs: Any) -> Dict[str, AgentResult]:
        """
        Coordinate execution of multiple agents.

        Keyword Arguments
        -----------------
        agents : list[str]
            Agent IDs to execute in sequence.
        """
        agent_ids: List[str] = kwargs.get("agents", [])
        results: Dict[str, AgentResult] = {}

        for agent_id in agent_ids:
            results[agent_id] = self.coordinate(agent_id, context, **kwargs)

        context.set_output(self.agent_id, results)
        return results

    # ========================================================
    # COORDINATOR UTILITIES
    # ========================================================

    def coordinator_ready(self) -> bool:
        """Determine whether the coordinator is ready for execution."""
        return self.manager is not None

    def agent_count(self) -> int:
        """Return the number of managed agents."""
        return self.manager.count()

    def agent_names(self) -> List[str]:
        """Return managed agent IDs."""
        return self.manager.names()

    def has_agent(self, agent_id: str) -> bool:
        """Determine whether the specified agent is managed."""
        return self.manager.contains(agent_id)

    def reset(self) -> None:
        """Reset the coordinator and its underlying manager."""
        self.manager.clear()
        self.metadata.clear()

    def get_capabilities(self) -> List[str]:
        """Return supported capabilities."""
        return [
            "agent_coordination",
            "multi_agent_execution",
            "workflow_management",
            "result_aggregation",
        ]

    def supports(self, capability: str) -> bool:
        """Determine whether a capability is supported."""
        return capability in self.get_capabilities()

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the coordinator agent."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "coordinator_ready": self.coordinator_ready(),
            "agent_count": self.agent_count(),
            "agents": self.agent_names(),
            "supported_capabilities": self.get_capabilities(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """Serialize the coordinator agent to JSON."""
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"CoordinatorAgent({self.agent_count()} agents)"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"<CoordinatorAgent id='{self.agent_id}' agents={self.agent_count()}>"