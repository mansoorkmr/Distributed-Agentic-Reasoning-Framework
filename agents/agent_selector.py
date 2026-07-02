"""
Distributed Agentic Reasoning Framework (DARF)
Agent Runtime

Agent Selector

Purpose
-------
Selects the most appropriate agent from the registry
for a given execution task.

Responsibilities
----------------
- Agent selection
- Capability matching
- Registry lookup
- Selection statistics

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
from dataclasses import field

from typing import Any
from typing import Dict
from typing import Optional

from agents.agent import Agent
from agents.agent_registry import AgentRegistry
from execution.execution_plan import ExecutionTask

__all__ = [
    "AgentSelector",
]
# ============================================================
# AGENT SELECTOR
# ============================================================


@dataclass(slots=True)
class AgentSelector:
    """
    Canonical DARF agent selector.
    """

    registry: AgentRegistry

    selections: int = 0

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
        # ========================================================
    # SELECTION
    # ========================================================

    def select(
        self,
        task: ExecutionTask,
    ) -> Optional[Agent]:
        """
        Select the best agent for a task.
        """

        self.selections += 1

        #
        # First preference:
        # task_name -> capability
        #

        matches = self.registry.find_by_capability(
            task.task_name
        )

        if matches:

            return matches[0]

        #
        # Second preference:
        # agent name
        #

        return self.registry.find_by_name(
            task.task_name
        )
        # ========================================================
    # HELPERS
    # ========================================================

    def selection_count(
        self,
    ) -> int:

        return self.selections

    def has_agents(
        self,
    ) -> bool:

        return not self.registry.is_empty()
        # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[
        str,
        Any,
    ]:

        return {

            "selection_count": self.selections,

            "registered_agents": self.registry.count(),

            "metadata": self.metadata,

            "version": self.version,

        }

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
            f"AgentSelector("
            f"{self.registry.count()} agents)"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<AgentSelector "
            f"selections={self.selections}>"
        )