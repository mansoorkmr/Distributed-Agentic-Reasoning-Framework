"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Execution Metrics

Purpose
-------
Defines the canonical execution metrics used by the
DARF Execution Fabric.

Responsibilities
----------------
- Collect execution statistics
- Compute success/failure metrics
- Measure execution durations
- Export runtime metrics

Design Principles
-----------------
- Read-only aggregation
- Stateless calculations
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

from execution.execution_result import ExecutionResult

__all__ = [
    "ExecutionMetrics",
]
# ============================================================
# EXECUTION METRICS
# ============================================================


@dataclass(slots=True)
class ExecutionMetrics:
    """
    Canonical execution metrics.
    """

    results: List[
        ExecutionResult
    ] = field(
        default_factory=list,
    )

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict,
    )

    version: str = "1.0"
        # ========================================================
    # RECORDING
    # ========================================================

    def add_result(
        self,
        result: ExecutionResult,
    ) -> None:
        """
        Record an execution result.
        """

        self.results.append(
            result,
        )
            # ========================================================
    # METRICS
    # ========================================================

    def execution_count(
        self,
    ) -> int:
        """
        Total executions.
        """

        return len(
            self.results,
        )

    def success_count(
        self,
    ) -> int:
        """
        Successful executions.
        """

        return sum(
            result.success
            for result in self.results
        )

    def failure_count(
        self,
    ) -> int:
        """
        Failed executions.
        """

        return (
            self.execution_count()
            - self.success_count()
        )

    def success_rate(
        self,
    ) -> float:
        """
        Success rate.
        """

        total = self.execution_count()

        if total == 0:
            return 1.0

        return (
            self.success_count()
            / total
        )

    def failure_rate(
        self,
    ) -> float:
        """
        Failure rate.
        """

        total = self.execution_count()

        if total == 0:
            return 0.0

        return (
            self.failure_count()
            / total
        )
        # ========================================================
    # DURATIONS
    # ========================================================

    def total_duration(
        self,
    ) -> float:
        """
        Total execution duration.
        """

        return sum(
            result.duration or 0.0
            for result in self.results
        )

    def average_duration(
        self,
    ) -> float:
        """
        Average execution duration.
        """

        total = self.execution_count()

        if total == 0:
            return 0.0

        return (
            self.total_duration()
            / total
        )
        # ========================================================
    # HELPERS
    # ========================================================

    def has_failures(
        self,
    ) -> bool:
        """
        Determine whether any execution failed.
        """

        return self.failure_count() > 0

    def reset(
        self,
    ) -> None:
        """
        Clear all collected metrics.
        """

        self.results.clear()
            # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[
        str,
        Any,
    ]:
        """
        Serialize execution metrics.
        """

        return {
            "execution_count": self.execution_count(),
            "success_count": self.success_count(),
            "failure_count": self.failure_count(),
            "success_rate": self.success_rate(),
            "failure_rate": self.failure_rate(),
            "total_duration": self.total_duration(),
            "average_duration": self.average_duration(),
            "has_failures": self.has_failures(),
            "version": self.version,
        }

    def to_json(
        self,
    ) -> str:
        """
        Serialize execution metrics to JSON.
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

        return (
            f"ExecutionMetrics("
            f"{self.execution_count()} executions)"
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"<ExecutionMetrics "
            f"executions={self.execution_count()} "
            f"success={self.success_count()} "
            f"failed={self.failure_count()}>"
        )