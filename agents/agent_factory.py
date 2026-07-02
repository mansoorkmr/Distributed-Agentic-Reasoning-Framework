"""
Distributed Agentic Reasoning Framework (DARF)
Agent Runtime

Agent Factory

Purpose
-------
Constructs DARF agents.

Responsibilities
----------------
- Agent creation
- Default configuration
- Capability attachment
- Runtime initialization

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
from typing import List

from agents.agent import Agent
from agents.agent_capability import AgentCapability

__all__ = [
    "AgentFactory",
]
# ============================================================
# AGENT FACTORY
# ============================================================


@dataclass(slots=True)
class AgentFactory:
    """
    Canonical DARF agent factory.
    """

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
        # ========================================================
    # FACTORY
    # ========================================================

    def create(
        self,
        name: str,
        description: str = "",
        capabilities: List[
            str
        ] | None = None,
    ) -> Agent:

        agent = Agent(

            name=name,

            description=description,

        )

        if capabilities:

            for capability in capabilities:

                agent.add_capability(

                    AgentCapability(

                        name=capability,

                    )

                )

        return agent
        # ========================================================
    # HELPERS
    # ========================================================

    def create_reasoning_agent(
        self,
    ) -> Agent:

        return self.create(

            name="Reasoner",

            capabilities=[

                "reasoning",

            ],

        )

    def create_planner_agent(
        self,
    ) -> Agent:

        return self.create(

            name="Planner",

            capabilities=[

                "planning",

            ],

        )

    def create_executor_agent(
        self,
    ) -> Agent:

        return self.create(

            name="Executor",

            capabilities=[

                "execution",

            ],

        )

    def create_tool_agent(
        self,
    ) -> Agent:

        return self.create(

            name="Tool",

            capabilities=[

                "tool",

            ],

        )
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

        return "AgentFactory"

    def __repr__(
        self,
    ) -> str:

        return "<AgentFactory>"