"""
Distributed Agentic Reasoning Framework (DARF)

Planner Metrics
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class PlannerMetrics:

    plans_created: int = 0

    successful_plans: int = 0

    failed_plans: int = 0

    tasks_generated: int = 0

    dependency_graphs: int = 0

    optimization_runs: int = 0

    metadata: dict = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # Recording
    # ---------------------------------------------------------

    def record_plan(
        self,
        success: bool,
        task_count: int = 0,
    ) -> None:

        self.plans_created += 1

        self.tasks_generated += task_count

        if success:

            self.successful_plans += 1

        else:

            self.failed_plans += 1

    def record_dependency_graph(
        self,
    ) -> None:

        self.dependency_graphs += 1

    def record_optimization(
        self,
    ) -> None:

        self.optimization_runs += 1

    def reset(
        self,
    ) -> None:

        self.plans_created = 0

        self.successful_plans = 0

        self.failed_plans = 0

        self.tasks_generated = 0

        self.dependency_graphs = 0

        self.optimization_runs = 0

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def success_rate(
        self,
    ) -> float:

        if self.plans_created == 0:

            return 0.0

        return (

            self.successful_plans

            / self.plans_created

        )

    def failure_rate(
        self,
    ) -> float:

        if self.plans_created == 0:

            return 0.0

        return (

            self.failed_plans

            / self.plans_created

        )

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "plans_created": self.plans_created,

            "successful_plans": self.successful_plans,

            "failed_plans": self.failed_plans,

            "tasks_generated": self.tasks_generated,

            "dependency_graphs": self.dependency_graphs,

            "optimization_runs": self.optimization_runs,

            "success_rate": self.success_rate(),

            "failure_rate": self.failure_rate(),

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(self):

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(self):

        return (

            f"PlannerMetrics(plans={self.plans_created})"

        )

    def __repr__(self):

        return (

            "<PlannerMetrics "

            f"plans={self.plans_created}>"

        )