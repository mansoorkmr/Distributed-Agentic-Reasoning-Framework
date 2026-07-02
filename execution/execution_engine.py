"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Execution Engine

Purpose
-------
Defines the canonical execution engine used by the
DARF Execution Fabric.

The execution engine is the public entry point
for executing execution plans.

Responsibilities
----------------
- Execute execution plans
- Coordinate executor
- Collect execution metrics
- Return execution results

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

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Callable
from typing import Dict
from typing import List

from execution.execution_metrics import ExecutionMetrics
from execution.execution_plan import ExecutionPlan
from execution.execution_result import ExecutionResult
from execution.executor import Executor

__all__ = [
    "ExecutionEngine",
]
# ============================================================
# EXECUTION ENGINE
# ============================================================


@dataclass(slots=True)
class ExecutionEngine:
    """
    Canonical execution engine.
    """

    metrics: ExecutionMetrics = field(
        default_factory=ExecutionMetrics,
    )

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
    )

    version: str = "1.0"
        # ========================================================
    # EXECUTION
    # ========================================================

    def execute(
        self,
        plan: ExecutionPlan,
        callables: Dict[
            str,
            Callable[..., Any],
        ],
    ) -> List[
        ExecutionResult
    ]:
        """
        Execute an execution plan.
        """

        executor = Executor(
            plan,
        )

        results = executor.execute(
            callables,
        )

        self.metrics.reset()

        for result in results:

            self.metrics.add_result(
                result,
            )

        return results
        # ========================================================
    # METRICS
    # ========================================================

    def execution_count(
        self,
    ) -> int:
        return self.metrics.execution_count()

    def success_count(
        self,
    ) -> int:
        return self.metrics.success_count()

    def failure_count(
        self,
    ) -> int:
        return self.metrics.failure_count()

    def success_rate(
        self,
    ) -> float:
        return self.metrics.success_rate()
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
            "metrics": self.metrics.to_dict(),
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
            f"ExecutionEngine("
            f"{self.execution_count()} executions)"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<ExecutionEngine "
            f"executions={self.execution_count()} "
            f"success={self.success_count()} "
            f"failed={self.failure_count()}>"
        )
    