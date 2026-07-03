"""
Distributed Agentic Reasoning Framework (DARF)

Planner Context
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import Optional

from execution.execution_plan import ExecutionPlan


@dataclass(slots=True)
class PlannerContext:

    request: Optional[str] = None

    goal: Optional[str] = None

    execution_plan: Optional[ExecutionPlan] = None

    variables: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # Variables
    # ---------------------------------------------------------

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.variables[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.variables.get(
            key,
            default,
        )

    def remove(
        self,
        key: str,
    ) -> None:

        self.variables.pop(
            key,
            None,
        )

    def contains(
        self,
        key: str,
    ) -> bool:

        return key in self.variables

    def variable_count(
        self,
    ) -> int:

        return len(self.variables)

    def is_empty(
        self,
    ) -> bool:

        return self.variable_count() == 0

    def clear(
        self,
    ) -> None:

        self.variables.clear()

    # ---------------------------------------------------------
    # Execution Plan
    # ---------------------------------------------------------

    def set_plan(
        self,
        plan: ExecutionPlan,
    ) -> None:

        self.execution_plan = plan

    def has_plan(
        self,
    ) -> bool:

        return self.execution_plan is not None

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "request": self.request,

            "goal": self.goal,

            "execution_plan":

                str(self.execution_plan)

                if self.execution_plan

                else None,

            "variables": self.variables,

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(self):

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

            default=str,

        )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(self):

        return (

            f"PlannerContext({self.variable_count()} variables)"

        )

    def __repr__(self):

        return (

            "<PlannerContext "

            f"variables={self.variable_count()}>"

        )