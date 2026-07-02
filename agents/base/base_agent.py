"""
Distributed Agentic Reasoning Framework (DARF)
Agent Runtime

Base Agent

Purpose
-------
Defines the runtime base class used by all DARF
agents.

Responsibilities
----------------
- Agent lifecycle
- Execution wrapper
- Common helper methods
- Runtime extension point

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json

from dataclasses import dataclass

from typing import Any
from typing import Dict

from agents.agent import Agent
from agents.agent_result import AgentResult

__all__ = [
    "BaseAgent",
]
# ============================================================
# BASE AGENT
# ============================================================


@dataclass(slots=True)
class BaseAgent(
    Agent,
):
    """
    Base runtime agent.
    """
        # ========================================================
    # LIFECYCLE
    # ========================================================

    def before_execute(
        self,
    ) -> None:
        """
        Hook executed before execution.
        """

        pass

    def after_execute(
        self,
        result: AgentResult,
    ) -> None:
        """
        Hook executed after execution.
        """

        pass
        # ========================================================
    # EXECUTION
    # ========================================================

    def run(
        self,
    ) -> AgentResult:
        """
        Execute the runtime agent.
        """

        self.before_execute()

        result = self.execute()

        self.after_execute(
            result,
        )

        return result
        # ========================================================
    # HELPERS
    # ========================================================

    def reset_context(
        self,
    ) -> None:

        self.context.clear()
            # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[
        str,
        Any,
    ]:

        return super(BaseAgent, self).to_dict()

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

        return (
            f"BaseAgent("
            f"{self.name})"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<BaseAgent "
            f"name='{self.name}'>"
        )