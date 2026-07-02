"""
Distributed Agentic Reasoning Framework (DARF)
Planner

Cost Estimator

Purpose
-------
Defines the canonical cost estimator used by the
DARF Planner.

The estimator provides lightweight estimates of
execution complexity before scheduling.

Responsibilities
----------------
- Estimate execution cost
- Estimate dependency cost
- Estimate execution depth
- Serialization

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
    "CostEstimator",
]
# ============================================================
# COST ESTIMATOR
# ============================================================


@dataclass(slots=True)
class CostEstimator:
    """
    Canonical execution cost estimator.
    """

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
        # ========================================================
    # ESTIMATION
    # ========================================================

    def estimate(
        self,
        plan: ExecutionPlan,
    ) -> float:
        """
        Estimate execution cost.

        Version 1:
        cost = tasks + dependencies
        """

        task_cost = len(
            plan.tasks
        )

        dependency_cost = sum(
            len(task.dependencies)
            for task in plan.tasks
        )

        return float(
            task_cost
            + dependency_cost
        )
        # ========================================================
    # HELPERS
    # ========================================================

    def task_cost(
        self,
        plan: ExecutionPlan,
    ) -> int:

        return len(
            plan.tasks
        )

    def dependency_cost(
        self,
        plan: ExecutionPlan,
    ) -> int:

        return sum(
            len(task.dependencies)
            for task in plan.tasks
        )

    def average_cost_per_task(
        self,
        plan: ExecutionPlan,
    ) -> float:

        if not plan.tasks:
            return 0.0

        return (
            self.estimate(plan)
            / len(plan.tasks)
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

        return "CostEstimator"

    def __repr__(
        self,
    ) -> str:

        return "<CostEstimator>"