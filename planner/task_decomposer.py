"""
Distributed Agentic Reasoning Framework (DARF)
Planner

Task Decomposer

Purpose
-------
Defines the canonical task decomposer used by the
DARF Planner.

The task decomposer converts high-level planning
requests into executable tasks.

Responsibilities
----------------
- Request decomposition
- Task generation
- Initial dependency assignment

Design Principles
-----------------
- Deterministic decomposition
- Extensible architecture
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
    "TaskDecomposer",
]
# ============================================================
# TASK DECOMPOSER
# ============================================================


@dataclass(slots=True)
class TaskDecomposer:
    """
    Canonical task decomposer.
    """

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
        # ========================================================
    # DECOMPOSITION
    # ========================================================

    def decompose(
        self,
        request: str,
    ) -> List[
        ExecutionTask
    ]:
        """
        Decompose a planning request
        into execution tasks.
        """

        task = ExecutionTask(
            task_name=request,
        )

        return [
            task,
        ]
        # ========================================================
    # HELPERS
    # ========================================================

    def task_count(
        self,
        request: str,
    ) -> int:
        """
        Return number of generated tasks.
        """

        return len(
            self.decompose(
                request,
            )
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

        return "TaskDecomposer"

    def __repr__(
        self,
    ) -> str:

        return "<TaskDecomposer>"
    