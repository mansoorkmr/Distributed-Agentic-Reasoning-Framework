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
import time

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict

from execution.execution_plan import ExecutionPlan

from planner.planning_policy import PlanningPolicy
from planner.planning_result import PlanningResult

# Step 1: New imports added here
from planner.task_decomposer import TaskDecomposer
from planner.dependency_resolver import DependencyResolver
from planner.plan_validator import PlanValidator
from planner.cost_estimator import CostEstimator
from planner.planning_graph import PlanningGraph

__all__ = [
    "Planner",
]
# ============================================================
# PLANNER
# ============================================================


@dataclass(slots=True)
class Planner:
    """
    Canonical planner.
    """

    policy: PlanningPolicy = field(
        default_factory=PlanningPolicy
    )

    # Step 2: New components added here
    decomposer: TaskDecomposer = field(
        default_factory=TaskDecomposer
    )

    resolver: DependencyResolver = field(
        default_factory=DependencyResolver
    )

    validator: PlanValidator = field(
        default_factory=PlanValidator
    )

    estimator: CostEstimator = field(
        default_factory=CostEstimator
    )

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
    
    # ========================================================
    # PLANNING
    # ========================================================

    # Step 3: Replaced plan() completely
    def plan(
        self,
        request: str,
    ) -> PlanningResult:
        """
        Produce an execution plan.
        """

        start = time.perf_counter()

        result = PlanningResult()

        try:

            tasks = self.decomposer.decompose(
                request,
            )

            tasks = self.resolver.resolve(
                tasks,
            )

            plan = ExecutionPlan()

            for task in tasks:

                plan.add_task(
                    task,
                )

            if tasks:

                plan.root_task = (
                    tasks[0].task_id
                )

            self.validator.validate(
                plan,
            )

            graph = PlanningGraph(
                plan,
            )

            cost = self.estimator.estimate(
                plan,
            )

            plan.metadata.update(
                {
                    "request": request,
                    "estimated_cost": cost,
                    "planning_graph_nodes": (
                        graph.node_count()
                    ),
                    "planning_graph_edges": (
                        graph.edge_count()
                    ),
                }
            )

            result.mark_success(
                plan,
            )

            result.planning_time = (
                time.perf_counter()
                - start
            )

        except Exception as exc:

            result.mark_failure(
                str(exc)
            )

        return result
        
    # ========================================================
    # SERIALIZATION
    # ========================================================

    # Step 4: Upgraded to_dict()
    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "policy": self.policy.to_dict(),
            "decomposer": self.decomposer.to_dict(),
            "resolver": self.resolver.to_dict(),
            "validator": self.validator.to_dict(),
            "estimator": self.estimator.to_dict(),
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
            f"Planner("
            f"depth={self.policy.max_depth})"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<Planner "
            f"parallel={self.policy.allow_parallelism}>"
        )