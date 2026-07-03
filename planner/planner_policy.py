"""
Distributed Agentic Reasoning Framework (DARF)

Planner Policy
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class PlannerPolicy:

    max_depth: int = 32

    max_tasks: int = 100

    enable_parallel_planning: bool = True

    enable_dependency_resolution: bool = True

    enable_optimization: bool = True

    optimization_strategy: str = "cost"

    planning_timeout: float = 30.0

    metadata: dict = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------

    def parallel_enabled(self) -> bool:

        return self.enable_parallel_planning

    def dependency_resolution_enabled(self) -> bool:

        return self.enable_dependency_resolution

    def optimization_enabled(self) -> bool:

        return self.enable_optimization

    def valid_depth(
        self,
        depth: int,
    ) -> bool:

        return depth <= self.max_depth

    def valid_task_count(
        self,
        count: int,
    ) -> bool:

        return count <= self.max_tasks

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "max_depth": self.max_depth,

            "max_tasks": self.max_tasks,

            "enable_parallel_planning":
                self.enable_parallel_planning,

            "enable_dependency_resolution":
                self.enable_dependency_resolution,

            "enable_optimization":
                self.enable_optimization,

            "optimization_strategy":
                self.optimization_strategy,

            "planning_timeout":
                self.planning_timeout,

            "metadata":
                self.metadata,

            "version":
                self.version,

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

            f"PlannerPolicy(depth={self.max_depth})"

        )

    def __repr__(self):

        return (

            "<PlannerPolicy "

            f"depth={self.max_depth} "

            f"tasks={self.max_tasks}>"

        )