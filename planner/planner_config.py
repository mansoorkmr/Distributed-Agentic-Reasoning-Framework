"""
Distributed Agentic Reasoning Framework (DARF)

Planner Configuration
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class PlannerConfig:

    max_planning_depth: int = 32

    max_tasks: int = 100

    enable_parallel_planning: bool = True

    enable_dependency_analysis: bool = True

    enable_heuristics: bool = True

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

    def dependency_analysis_enabled(self) -> bool:

        return self.enable_dependency_analysis

    def heuristics_enabled(self) -> bool:

        return self.enable_heuristics

    def within_depth(
        self,
        depth: int,
    ) -> bool:

        return depth <= self.max_planning_depth

    def within_task_limit(
        self,
        tasks: int,
    ) -> bool:

        return tasks <= self.max_tasks

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "max_planning_depth": self.max_planning_depth,

            "max_tasks": self.max_tasks,

            "enable_parallel_planning":
                self.enable_parallel_planning,

            "enable_dependency_analysis":
                self.enable_dependency_analysis,

            "enable_heuristics":
                self.enable_heuristics,

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

            f"PlannerConfig(depth={self.max_planning_depth})"

        )

    def __repr__(self):

        return (

            "<PlannerConfig "

            f"depth={self.max_planning_depth} "

            f"tasks={self.max_tasks}>"

        )