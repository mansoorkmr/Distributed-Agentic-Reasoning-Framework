"""
Distributed Agentic Reasoning Framework (DARF)

Planner Agent

Purpose
-------
Canonical planning agent.

Responsibilities
----------------
- Request decomposition
- Execution plan generation
- Planning orchestration

Thread Safety
-------------
Thread-safe.
"""

from __future__ import annotations

import json

from dataclasses import dataclass, field

from typing import Any
from typing import Dict

from agents.base.base_agent import BaseAgent
from agents.agent_capability import AgentCapability
from agents.agent_result import AgentResult

from planner.planner import Planner

__all__ = [
    "PlannerAgent",
]
# ============================================================
# PLANNER AGENT
# ============================================================


@dataclass(slots=True)
class PlannerAgent(
    BaseAgent,
):
    """
    Canonical planner agent.
    """

    planner: Planner = field(default_factory=Planner)

    def __post_init__(
        self,
    ) -> None:

        super(PlannerAgent, self).__post_init__()

        self.name = "Planner"

        if not self.has_capability(
            "planning",
        ):

            self.add_capability(

                AgentCapability(
                    name="planning",
                )

            )
            
    # ========================================================
    # EXECUTION
    # ========================================================

    def execute(
        self,
    ) -> AgentResult:

        result = AgentResult()

        result.agent_id = self.agent_id

        request = self.context.get(
            "request",
        )

        if request is None:

            result.mark_success(
                output=None,
            )

            return result

        planning = self.planner.plan(
            request,
        )

        result.mark_success(
            output=planning.execution_plan,
        )

        return result
        
    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[
        str,
        Any,
    ]:
        
        # FIX: Explicitly pass the class and instance to super()
        return super(PlannerAgent, self).to_dict()

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

        return "PlannerAgent"

    def __repr__(
        self,
    ) -> str:

        return "<PlannerAgent>"