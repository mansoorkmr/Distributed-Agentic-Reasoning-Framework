"""
Distributed Agentic Reasoning Framework (DARF)

Reasoning Agent

Purpose
-------
Canonical reasoning agent.

Responsibilities
----------------
- Logical reasoning
- Problem solving
- Knowledge inference

Thread Safety
-------------
Thread-safe.
"""

from __future__ import annotations

import json

from dataclasses import dataclass

from typing import Any
from typing import Dict

from agents.base.base_agent import BaseAgent
from agents.agent_capability import AgentCapability
from agents.agent_result import AgentResult

__all__ = [
    "ReasoningAgent",
]
# ============================================================
# REASONING AGENT
# ============================================================


@dataclass(slots=True)
class ReasoningAgent(
    BaseAgent,
):
    """
    Canonical reasoning agent.
    """

    def __post_init__(
        self,
    ) -> None:

        super(ReasoningAgent, self).__post_init__()

        self.name = "Reasoner"

        if not self.has_capability(
            "reasoning",
        ):

            self.add_capability(

                AgentCapability(
                    name="reasoning",
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

        question = self.context.get(
            "question",
        )

        if question is None:

            result.mark_success(
                output="No reasoning request.",
            )

            return result

        result.mark_success(

            output=f"Reasoned: {question}",

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

        return super(ReasoningAgent, self).to_dict()

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

        return "ReasoningAgent"

    def __repr__(
        self,
    ) -> str:

        return (

            "<ReasoningAgent>"

        )