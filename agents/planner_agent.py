"""
Distributed Agentic Reasoning Framework (DARF)

Planner Agent

Purpose
-------
Provides the canonical planning agent for DARF.

The PlannerAgent converts high-level user objectives
into executable ExecutionPlans using the Planner
subsystem.

Responsibilities
----------------
- Accept objectives
- Invoke Planner
- Produce ExecutionPlan
- Return AgentResult

Design Principles
-----------------
- Thin wrapper around Planner
- Stateless execution
- Shared AgentContext
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
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from agents.agent_context import AgentContext

from planner.planner import Planner
from planner.planner_result import PlannerResult

__all__ = ["PlannerAgent"]

# ============================================================
# PLANNER AGENT
# ============================================================

@dataclass(slots=True)
class PlannerAgent(BaseAgent):
    """
    Canonical DARF Planner Agent.
    Serves as the bridge between the Agent routing layer and the Planner subsystem.
    """

    id: str = "planner"
    name: str = "Planner Agent"
    description: str = "Generates execution plans from user objectives."
    version: str = "1.0"

    planner: Planner = field(default_factory=Planner)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ========================================================
    # EXECUTION
    # ========================================================

    def run(self, context: AgentContext, **kwargs: Any) -> PlannerResult:
        """
        Generate an execution plan from the supplied objective.
        """
        objective = kwargs.get("objective")

        if objective is None:
            objective = context.get("objective")

        if objective is None:
            raise ValueError("No planning objective supplied.")

        context.set("objective", objective)

        result = self.planner.plan(objective)
        context.set_output(self.agent_id, result)

        return result

    # ========================================================
    # PLANNER UTILITIES
    # ========================================================

    def planner_ready(self) -> bool:
        """Determine whether the planner is available."""
        return self.planner is not None

    def reset(self) -> None:
        """Reset planner state."""
        if hasattr(self.planner, "reset"):
            self.planner.reset()
        self.metadata.clear()

    def get_capabilities(self) -> List[str]:
        """Return planner specific capability tags."""
        return [
            "objective_planning",
            "task_decomposition",
            "execution_plan_generation",
            "dependency_analysis",
        ]

    def supports(self, capability: str) -> bool:
        """Determine whether a capability is supported."""
        return capability in self.get_capabilities()

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the planner agent."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "planner_ready": self.planner_ready(),
            "supported_capabilities": self.get_capabilities(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """Serialize the planner agent to JSON."""
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(self) -> str:
        return f"PlannerAgent(ready={self.planner_ready()})"

    def __repr__(self) -> str:
        return f"<PlannerAgent id='{self.agent_id}' ready={self.planner_ready()}>"