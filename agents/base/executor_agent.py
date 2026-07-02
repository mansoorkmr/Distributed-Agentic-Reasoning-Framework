"""
Distributed Agentic Reasoning Framework (DARF)

Executor Agent

Purpose
-------
Canonical execution agent.

Responsibilities
----------------
- Execute execution plans
- Coordinate execution engine
- Return execution results

Thread Safety
-------------
Thread-safe.
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict

from agents.base.base_agent import BaseAgent
from agents.agent_capability import AgentCapability
from agents.agent_result import AgentResult

from execution.execution_engine import ExecutionEngine
from execution.execution_plan import ExecutionPlan

__all__ = [
    "ExecutorAgent",
]
# ============================================================
# EXECUTOR AGENT
# ============================================================


@dataclass(slots=True)
class ExecutorAgent(
    BaseAgent,
):
    """
    Canonical executor agent.
    """

    engine: ExecutionEngine = field(
        default_factory=ExecutionEngine
    )

    def __post_init__(
        self,
    ) -> None:

        super(ExecutorAgent, self).__post_init__()

        self.name = "Executor"

        if not self.has_capability(
            "execution",
        ):

            self.add_capability(

                AgentCapability(
                    name="execution",
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

        plan = self.context.get(
            "execution_plan",
        )

        callables = self.context.get(
            "callables",
            {},
        )

        if not isinstance(
            plan,
            ExecutionPlan,
        ):

            result.mark_success(
                output=None,
            )

            return result

        results = self.engine.execute(
            plan,
            callables,
        )

        result.mark_success(
            output=results,
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

        return super(ExecutorAgent, self).to_dict()

    def to_json(
        self,
    ) -> str:

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,
            
            default=str,

        )
        # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(
        self,
    ) -> str:

        return "ExecutorAgent"

    def __repr__(
        self,
    ) -> str:

        return "<ExecutorAgent>"