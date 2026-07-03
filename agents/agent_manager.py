"""
Distributed Agentic Reasoning Framework (DARF)

Agent Manager

Purpose
-------
Defines the canonical Agent Manager responsible for
coordinating all agents within DARF.

Responsibilities
----------------
- Register and remove agents
- Execute agents (by instance or ID)
- Maintain shared agent context
- Collect and expose execution statistics
- Provide a unified, thread-safe agent API

Design Principles
-----------------
- Centralized coordination
- Composition over inheritance
- Shared execution state
- Production-ready observability

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
import time
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agents.agent import Agent
from agents.base_agent import BaseAgent
from agents.agent_context import AgentContext
from agents.agent_registry import AgentRegistry
from agents.agent_result import AgentResult

logger = logging.getLogger(__name__)

__all__ = ["AgentManager"]

# ============================================================
# AGENT MANAGER
# ============================================================

@dataclass(slots=True)
class AgentManager:
    """
    Canonical DARF Agent Manager.
    Orchestrates the lifecycle, context, and execution of all agents.
    """

    registry: AgentRegistry = field(default_factory=AgentRegistry)
    context: AgentContext = field(default_factory=AgentContext)

    # Statistics
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    # ========================================================
    # REGISTRATION
    # ========================================================

    def register(self, agent: Agent) -> None:
        """Register an agent into the manager's registry."""
        self.registry.register(agent)

    def unregister(self, agent_id: str) -> bool:
        """Remove an agent by ID. Returns True if successful."""
        return self.registry.unregister(agent_id)

    # ========================================================
    # LOOKUP
    # ========================================================

    def get(self, agent_id: str) -> Optional[Agent]:
        """Return a registered agent by ID."""
        return self.registry.get(agent_id)

    def contains(self, agent_id: str) -> bool:
        """Determine whether an agent exists in the registry."""
        return self.registry.contains(agent_id)

    # ========================================================
    # COLLECTION
    # ========================================================

    def names(self) -> List[str]:
        """Return a sorted list of registered agent IDs."""
        return self.registry.names()

    def agents(self) -> List[Agent]:
        """Return a list of all registered agent instances."""
        return self.registry.values()

    def count(self) -> int:
        """Return the number of registered agents."""
        return self.registry.count()

    def is_empty(self) -> bool:
        """Return True if no agents are registered."""
        return self.registry.is_empty()

    def clear(self) -> None:
        """Clear the registry, context, and reset all statistics."""
        self.registry.clear()
        self.context.clear()
        self.reset_statistics()
        self.metadata.clear()

    # ========================================================
    # EXECUTION
    # ========================================================

    def execute(self, agent: Agent, **kwargs: Any) -> AgentResult:
        """
        Execute an agent instance and track statistics.
        """
        if not isinstance(agent, Agent):
            raise TypeError("The 'agent' parameter must be an instance of Agent.")

        self.execution_count += 1
        start_time = time.perf_counter()

        try:
            # If it's a BaseAgent, it has built-in lifecycle and timing hooks
            if isinstance(agent, BaseAgent):
                result = agent.execute(self.context, **kwargs)
            else:
                # Fallback for bare Agents: manually update context and calculate timing
                self.context.current_agent = agent.agent_id
                output = agent.run(self.context, **kwargs)
                self.context.set_output(agent.agent_id, output)

                duration = time.perf_counter() - start_time
                result = AgentResult(
                    agent_id=agent.agent_id,
                    success=True,
                    output=output,
                    execution_time=duration,
                )

        except Exception as exc:
            duration = time.perf_counter() - start_time
            logger.error(f"Execution failed for agent '{agent.agent_id}': {exc}")
            result = AgentResult(
                agent_id=agent.agent_id,
                success=False,
                error=str(exc),
                execution_time=duration,
            )

        # Update statistics based on the final result
        if result.success:
            self.success_count += 1
        else:
            self.failure_count += 1

        return result

    def execute_by_id(self, agent_id: str, **kwargs: Any) -> AgentResult:
        """
        Execute a registered agent by its ID.
        """
        agent = self.get(agent_id)
        if agent is None:
            raise ValueError(f"Unknown agent '{agent_id}'.")

        return self.execute(agent, **kwargs)

    # ========================================================
    # STATISTICS
    # ========================================================

    def successful_executions(self) -> int:
        return self.success_count

    def failed_executions(self) -> int:
        return self.failure_count

    def total_executions(self) -> int:
        return self.execution_count

    def success_rate(self) -> float:
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count

    def failure_rate(self) -> float:
        if self.execution_count == 0:
            return 0.0
        return self.failure_count / self.execution_count

    def reset_statistics(self) -> None:
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_count": self.count(),
            "agents": self.names(),
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": round(self.success_rate(), 4),
            "failure_rate": round(self.failure_rate(), 4),
            "context": self.context.to_dict(),
            "registry": self.registry.to_dict(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __len__(self) -> int:
        return self.count()

    def __contains__(self, agent_id: str) -> bool:
        return self.contains(agent_id)

    def __str__(self) -> str:
        return f"AgentManager({self.count()} agents, {self.execution_count} executions)"

    def __repr__(self) -> str:
        return (
            f"<AgentManager "
            f"agents={self.count()} "
            f"executions={self.execution_count} "
            f"success={self.success_count} "
            f"failed={self.failure_count}>"
        )