"""
Distributed Agentic Reasoning Framework (DARF)
Planner

Dependency Resolver

Purpose
-------
Defines the canonical dependency resolver used by the
DARF Planner.

The dependency resolver validates and resolves task
dependencies before execution.

Responsibilities
----------------
- Dependency validation
- Dependency resolution
- Task relationship verification

Design Principles
-----------------
- Deterministic validation
- Strong typing
- Production-ready serialization

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
from typing import List

from execution.execution_plan import ExecutionTask

__all__ = [
    "DependencyResolver",
]
# ============================================================
# DEPENDENCY RESOLVER
# ============================================================


@dataclass(slots=True)
class DependencyResolver:
    """
    Canonical dependency resolver.
    """

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
        # ========================================================
    # DEPENDENCY VALIDATION
    # ========================================================

    def validate(
        self,
        tasks: List[
            ExecutionTask
        ],
    ) -> bool:
        """
        Validate task dependencies.
        """

        task_ids = {
            task.task_id
            for task in tasks
        }

        for task in tasks:

            for dependency in task.dependencies:

                if dependency not in task_ids:

                    raise ValueError(
                        f"Unknown dependency '{dependency}'."
                    )

        return True
        # ========================================================
    # RESOLUTION
    # ========================================================

    def resolve(
        self,
        tasks: List[
            ExecutionTask
        ],
    ) -> List[
        ExecutionTask
    ]:
        """
        Resolve task dependencies.
        """

        self.validate(
            tasks,
        )

        return tasks
        # ========================================================
    # HELPERS
    # ========================================================

    def dependency_count(
        self,
        tasks: List[
            ExecutionTask
        ],
    ) -> int:
        """
        Return total number of dependencies.
        """

        return sum(
            len(task.dependencies)
            for task in tasks
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

        return "DependencyResolver"

    def __repr__(
        self,
    ) -> str:

        return "<DependencyResolver>"
    