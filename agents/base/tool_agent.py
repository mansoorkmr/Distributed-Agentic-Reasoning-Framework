"""
Distributed Agentic Reasoning Framework (DARF)

Tool Agent

Purpose
-------
Canonical tool execution agent.

Responsibilities
----------------
- Execute tools
- Invoke callable tools
- Return tool outputs

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
    "ToolAgent",
]
# ============================================================
# TOOL AGENT
# ============================================================


@dataclass(slots=True)
class ToolAgent(
    BaseAgent,
):
    """
    Canonical tool execution agent.
    """

    def __post_init__(
        self,
    ) -> None:

        super(ToolAgent, self).__post_init__()

        self.name = "Tool"

        if not self.has_capability(
            "tool",
        ):

            self.add_capability(

                AgentCapability(
                    name="tool",
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

        tool = self.context.get(
            "tool",
        )

        arguments = self.context.get(
            "arguments",
            {},
        )

        if tool is None:

            result.mark_success(
                output=None,
            )

            return result

        if not callable(
            tool,
        ):

            result.mark_failure(
                "Object is not callable.",
            )

            return result

        output = tool(
            **arguments,
        )

        result.mark_success(
            output=output,
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

        return super(ToolAgent, self).to_dict()

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

        return "ToolAgent"

    def __repr__(
        self,
    ) -> str:

        return "<ToolAgent>"