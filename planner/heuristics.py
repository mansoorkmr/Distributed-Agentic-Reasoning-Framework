"""
Distributed Agentic Reasoning Framework (DARF)
Planner

Planning Heuristics

Purpose
-------
Defines the canonical heuristics used by the DARF Planner
to evaluate, prioritize, and cost execution plans.

Responsibilities
----------------
- Task prioritization
- Cost estimation
- Plan depth estimation

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict

# Both classes are correctly imported from the execution_plan module
from execution.execution_plan import ExecutionPlan
from execution.execution_plan import ExecutionTask

__all__ = [
    "Heuristics",
]


# ============================================================
# PLANNING HEURISTICS
# ============================================================

@dataclass(slots=True)
class Heuristics:
    """
    Canonical planning heuristics engine.
    """

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ========================================================
    # PLAN OPTIMIZATION
    # ========================================================

    def prioritize(
        self,
        plan: ExecutionPlan,
    ) -> ExecutionPlan:
        """
        Sort tasks in the execution plan in-place based on 
        priority (highest priority first).
        """
        plan.tasks.sort(
            key=lambda task: task.priority,
            reverse=True,
        )

        return plan

    # ========================================================
    # ESTIMATIONS
    # ========================================================

    def estimated_cost(
        self,
        plan: ExecutionPlan,
    ) -> int:
        """
        Calculate the estimated computational or temporal 
        cost of the execution plan.
        """
        return plan.task_count()

    def estimated_depth(
        self,
        plan: ExecutionPlan,
    ) -> int:
        """
        Calculate the estimated execution depth 
        (longest path of dependencies) of the plan.
        """
        return plan.task_count()

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Serialize the heuristics state to a dictionary.
        """
        return {
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(
        self,
    ) -> str:
        """
        Serialize the heuristics state to a formatted JSON string.
        """
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
        """
        Human-readable representation.
        """
        return "Heuristics"

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """
        return f"<Heuristics version='{self.version}'>"