"""
Distributed Agentic Reasoning Framework (DARF)
Planner

Planner

Purpose
-------
Defines the canonical planner used by the
DARF Planner subsystem.

The planner converts planning requests into
canonical execution plans.

Responsibilities
----------------
- Create execution plans
- Coordinate planning components
- Produce planning results
- Apply planning policy
- Track planning metrics

Design Principles
-----------------
- High-level orchestration
- Composition over inheritance
- Thin façade
- Production-ready

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

from execution.execution_plan import ExecutionPlan

# Core planner orchestration components
from planner.planner_config import PlannerConfig
from planner.planner_context import PlannerContext
from planner.planner_metrics import PlannerMetrics
from planner.planner_policy import PlannerPolicy
from planner.planner_registry import PlannerRegistry
from planner.planner_result import PlannerResult

# Planning intelligence components
from planner.task_decomposer import TaskDecomposer
from planner.dependency_graph import DependencyGraph
from planner.heuristics import Heuristics

__all__ = [
    "Planner",
]


# ============================================================
# PLANNER
# ============================================================

@dataclass(slots=True)
class Planner:
    """
    Canonical planner orchestrator.
    """

    config: PlannerConfig = field(
        default_factory=PlannerConfig
    )

    context: PlannerContext = field(
        default_factory=PlannerContext
    )

    policy: PlannerPolicy = field(
        default_factory=PlannerPolicy
    )

    metrics: PlannerMetrics = field(
        default_factory=PlannerMetrics
    )

    registry: PlannerRegistry = field(
        default_factory=PlannerRegistry
    )

    decomposer: TaskDecomposer = field(
        default_factory=TaskDecomposer
    )

    dependency_graph: DependencyGraph = field(
        default_factory=DependencyGraph
    )

    heuristics: Heuristics = field(
        default_factory=Heuristics
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ========================================================
    # PLANNING
    # ========================================================

    def plan(
        self,
        objective: str,
    ) -> PlannerResult:
        """
        Produce an execution plan based on the provided objective.
        """
        result = PlannerResult()

        if not objective:
            self.metrics.record_plan(
                False,
            )
            result.mark_failure(
                "Objective is empty."
            )
            return result

        # Decompose objective into an initial plan
        plan = self.decomposer.decompose(
            objective,
        )

        # Apply heuristics to prioritize tasks in-place
        plan = self.heuristics.prioritize(
            plan,
        )

        # Update execution context
        self.context.request = objective
        self.context.goal = objective
        self.context.set_plan(
            plan,
        )

        # Record system metrics
        self.metrics.record_plan(
            True,
            task_count=plan.task_count(),
        )
        self.metrics.record_dependency_graph()
        self.metrics.record_optimization()

        # Mark final success
        result.mark_success(
            plan,
        )

        return result

    # ========================================================
    # CONVENIENCE
    # ========================================================

    def task_count(
        self,
        objective: str,
    ) -> int:
        """
        Return the number of generated tasks for a given objective.
        """
        return self.decomposer.task_count(
            objective,
        )

    def reset(
        self,
    ) -> None:
        """
        Reset the planner context, metrics, and dependency graph.
        """
        self.context = PlannerContext()
        self.metrics.reset()
        self.dependency_graph.clear()

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Serialize the planner state to a dictionary.
        """
        return {
            "config": self.config.to_dict(),
            "context": self.context.to_dict(),
            "policy": self.policy.to_dict(),
            "metrics": self.metrics.to_dict(),
            "registry": self.registry.to_dict(),
            "dependency_graph": self.dependency_graph.to_dict(),
            "decomposer": self.decomposer.to_dict(),
            "heuristics": self.heuristics.to_dict(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(
        self,
    ) -> str:
        """
        Serialize the planner state to a formatted JSON string.
        """
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
        """
        Human-readable representation.
        """
        return f"Planner(depth={self.config.max_planning_depth})"

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """
        return f"<Planner plans={self.metrics.plans_created}>"