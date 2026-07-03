"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Dependency Resolver

Purpose
-------
Resolves task dependencies for execution plans.

Responsibilities
----------------
- Validate task dependencies
- Resolve dependency relationships
- Discover executable tasks
- Compute execution order
- Support scheduler and dispatcher

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
from typing import Any, Dict, List, Optional, Set

from execution.execution_plan import (
    ExecutionPlan,
    ExecutionTask,
)

__all__ = [
    "DependencyResolver",
]


# ============================================================
# DEPENDENCY RESOLVER
# ============================================================


@dataclass(slots=True)
class DependencyResolver:
    """
    Resolves task dependencies within an
    execution plan.
    """

    plan: ExecutionPlan

    metadata: Dict[str, Any] = field(
        default_factory=dict,
    )

    version: str = "1.0"

    def __post_init__(self) -> None:
        """
        Validate execution plan.
        """
        if not isinstance(self.plan, ExecutionPlan):
            raise TypeError("plan must be an ExecutionPlan.")

        self.plan.validate()

    # ============================================================
    # DEPENDENCY LOOKUP
    # ============================================================

    def build(self) -> "DependencyResolver":
        """
        Build and validate the dependency graph.

        Returns
        -------
        DependencyResolver
            The current resolver.
        """
        self.validate()
        return self

    def validate(self) -> None:
        """
        Validate all task dependencies.

        Raises
        ------
        ValueError
            If any dependency references
            a missing task.
        """
        task_ids = {
            task.task_id
            for task in self.plan.tasks
        }

        for task in self.plan.tasks:
            for dependency in task.dependencies:
                if dependency not in task_ids:
                    raise ValueError(
                        f"Task '{task.task_name}' "
                        f"depends on unknown task "
                        f"'{dependency}'."
                    )

    def task(self, task_id: str) -> Optional[ExecutionTask]:
        """
        Return a task by ID.
        """
        return self.plan.get_task(task_id)

    def contains(self, task_id: str) -> bool:
        """
        Determine whether a task exists.
        """
        return self.task(task_id) is not None

    def task_count(self) -> int:
        """
        Return total number of tasks.
        """
        return self.plan.task_count()

    # ============================================================
    # DEPENDENCY RESOLUTION
    # ============================================================

    def dependencies(self, task_id: str) -> List[str]:
        """
        Return the dependencies of a task.
        """
        task = self.task(task_id)
        if task is None:
            raise ValueError(f"Unknown task '{task_id}'.")

        return list(task.dependencies)

    def dependents(self, task_id: str) -> List[str]:
        """
        Return every task that depends
        on the given task.
        """
        if not self.contains(task_id):
            raise ValueError(f"Unknown task '{task_id}'.")

        result: List[str] = []

        for task in self.plan.tasks:
            if task_id in task.dependencies:
                result.append(task.task_id)

        return result

    def ready_tasks(self, completed_tasks: Set[str]) -> List[ExecutionTask]:
        """
        Return every task whose
        dependencies have been satisfied.
        """
        ready: List[ExecutionTask] = []

        for task in self.plan.tasks:
            if task.task_id in completed_tasks:
                continue

            if all(dependency in completed_tasks for dependency in task.dependencies):
                ready.append(task)

        return ready

    def blocked_tasks(self, completed_tasks: Set[str]) -> List[ExecutionTask]:
        """
        Return every task that is still
        waiting on dependencies.
        """
        blocked: List[ExecutionTask] = []

        for task in self.plan.tasks:
            if task.task_id in completed_tasks:
                continue

            if any(dependency not in completed_tasks for dependency in task.dependencies):
                blocked.append(task)

        return blocked

    # ============================================================
    # GRAPH ANALYSIS
    # ============================================================

    def topological_order(self) -> List[str]:
        """
        Return the tasks in topological
        execution order using Kahn's Algorithm.

        Raises
        ------
        ValueError
            If a dependency cycle exists.
        """
        indegree: Dict[str, int] = {
            task.task_id: 0
            for task in self.plan.tasks
        }

        adjacency: Dict[str, List[str]] = {
            task.task_id: []
            for task in self.plan.tasks
        }

        for task in self.plan.tasks:
            for dependency in task.dependencies:
                adjacency[dependency].append(task.task_id)
                indegree[task.task_id] += 1

        queue = [
            task_id
            for task_id, degree in indegree.items()
            if degree == 0
        ]

        order: List[str] = []

        while queue:
            current = queue.pop(0)
            order.append(current)

            for dependent in adjacency[current]:
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    queue.append(dependent)

        if len(order) != self.task_count():
            raise ValueError("Dependency cycle detected.")

        return order

    def execution_levels(self) -> List[List[str]]:
        """
        Return execution levels for parallel execution.

        Tasks within the same level
        may execute concurrently.
        """
        completed: Set[str] = set()
        levels: List[List[str]] = []

        while len(completed) < self.task_count():
            ready = [
                task.task_id
                for task in self.ready_tasks(completed)
            ]

            if not ready:
                raise ValueError("Dependency cycle detected.")

            levels.append(ready)
            completed.update(ready)

        return levels

    def root_tasks(self) -> List[str]:
        """
        Return tasks that have
        no dependencies.
        """
        return [
            task.task_id
            for task in self.plan.tasks
            if not task.dependencies
        ]

    def leaf_tasks(self) -> List[str]:
        """
        Return tasks that no other
        task depends upon.
        """
        depended_on: Set[str] = set()

        for task in self.plan.tasks:
            depended_on.update(task.dependencies)

        return [
            task.task_id
            for task in self.plan.tasks
            if task.task_id not in depended_on
        ]

    # ============================================================
    # UTILITY
    # ============================================================

    def clear(self) -> None:
        """
        Clear resolver metadata.

        The execution plan is intentionally
        preserved.
        """
        self.metadata.clear()

    # ============================================================
    # SERIALIZATION
    # ============================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the dependency resolver.
        """
        return {
            "task_count": self.task_count(),
            "root_tasks": self.root_tasks(),
            "leaf_tasks": self.leaf_tasks(),
            "topological_order": self.topological_order(),
            "execution_levels": self.execution_levels(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """
        Serialize the dependency
        resolver to JSON.
        """
        return json.dumps(
            self.to_dict(),
            indent=4,
            sort_keys=True,
        )

    # ============================================================
    # COLLECTION INTERFACE
    # ============================================================

    def __len__(self) -> int:
        """
        Return total number of tasks
        in the execution plan.
        """
        return self.task_count()

    def __contains__(self, task_id: str) -> bool:
        """
        Determine whether a task exists.
        """
        return self.contains(task_id)

    # ============================================================
    # REPRESENTATION
    # ============================================================

    def __str__(self) -> str:
        """
        Human-readable representation.
        """
        return f"DependencyResolver({self.task_count()} tasks)"

    def __repr__(self) -> str:
        """
        Developer representation.
        """
        return (
            f"<DependencyResolver "
            f"tasks={self.task_count()} "
            f"roots={len(self.root_tasks())} "
            f"leaves={len(self.leaf_tasks())}>"
        )