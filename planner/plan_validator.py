"""
Distributed Agentic Reasoning Framework (DARF)
Planner

Plan Validator

Purpose
-------
Defines the canonical execution plan validator.

Responsibilities
----------------
- Validate execution plans
- Verify task integrity
- Verify dependencies
- Verify root task

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

from execution.execution_plan import ExecutionPlan

__all__ = [
    "PlanValidator",
]
# ============================================================
# PLAN VALIDATOR
# ============================================================


@dataclass(slots=True)
class PlanValidator:
    """
    Canonical execution plan validator.
    """

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
        # ========================================================
    # VALIDATION
    # ========================================================

    def validate(
        self,
        plan: ExecutionPlan,
    ) -> bool:
        """
        Validate an execution plan.
        """

        if plan is None:

            raise ValueError(
                "Execution plan cannot be None."
            )

        task_ids = set()

        for task in plan.tasks:

            if not task.task_name.strip():

                raise ValueError(
                    "Task name cannot be empty."
                )

            if task.task_id in task_ids:

                raise ValueError(
                    f"Duplicate task '{task.task_id}'."
                )

            task_ids.add(
                task.task_id
            )

        for task in plan.tasks:

            for dependency in task.dependencies:

                if dependency not in task_ids:

                    raise ValueError(
                        f"Unknown dependency '{dependency}'."
                    )

        if (
            plan.root_task is not None
            and plan.root_task not in task_ids
        ):

            raise ValueError(
                "Root task does not exist."
            )

        return True
        # ========================================================
    # HELPERS
    # ========================================================

    def task_count(
        self,
        plan: ExecutionPlan,
    ) -> int:

        return len(
            plan.tasks
        )

    def is_empty(
        self,
        plan: ExecutionPlan,
    ) -> bool:

        return (
            self.task_count(plan)
            == 0
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

        return "PlanValidator"

    def __repr__(
        self,
    ) -> str:

        return "<PlanValidator>"