"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Execution Result

Purpose
-------
Defines the canonical execution result returned by every
execution component inside DARF.

Every execution performed by the framework returns an
ExecutionResult instance.

Responsibilities
----------------
- Execution lifecycle tracking
- Execution status reporting
- Timing information
- Metrics collection
- Structured serialization
- Error propagation
- Monitoring support

Design Principles
-----------------
- Immutable execution identity
- Strong typing
- JSON serialization
- Production logging support
- Distributed execution compatibility

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import uuid
import json
from dataclasses import dataclass
from dataclasses import field

from datetime import datetime
from datetime import timezone

from enum import Enum
from enum import unique

from typing import Any
from typing import Dict
from typing import Optional

from execution.exceptions import DARFExecutionError


# ============================================================
# EXECUTION STATUS
# ============================================================


@unique
class ExecutionStatus(
    str,
    Enum,
):
    """
    Current execution state.
    """

    CREATED = "created"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


# ============================================================
# EXECUTION OUTCOME
# ============================================================


@unique
class ExecutionOutcome(
    str,
    Enum,
):
    """
    Final execution outcome.
    """

    UNKNOWN = "unknown"

    SUCCESS = "success"

    FAILURE = "failure"

    CANCELLED = "cancelled"


# ============================================================
# EXECUTION RESULT
# ============================================================


@dataclass(
    slots=True,
)
class ExecutionResult:
    """
    Canonical execution result.

    Returned by every execution
    component inside DARF.
    """

    execution_id: str = field(
        default_factory=lambda:
        f"EXEC-{uuid.uuid4().hex.upper()}"
    )

    request_id: Optional[str] = None

    agent_id: Optional[str] = None

    task_name: Optional[str] = None

    status: ExecutionStatus = (
        ExecutionStatus.CREATED
    )

    outcome: ExecutionOutcome = (
        ExecutionOutcome.UNKNOWN
    )

    success: bool = False

    created_at: str = field(
        default_factory=lambda:
        datetime.now(
            timezone.utc
        ).isoformat(
            timespec="seconds"
        )
    )

    started_at: Optional[str] = None

    completed_at: Optional[str] = None

    duration: Optional[float] = None

    result: Any = None

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    metrics: Dict[
        str,
        float,
    ] = field(
        default_factory=dict
    )

    warnings: list[str] = field(
        default_factory=list
    )

    error: Optional[
        DARFExecutionError
    ] = None

    version: str = "1.0"
        # ========================================================
    # LIFECYCLE
    # ========================================================

    def mark_started(
        self,
    ) -> None:
        """
        Mark execution as started.
        """

        self.status = ExecutionStatus.RUNNING

        self.started_at = datetime.now(
            timezone.utc
        ).isoformat(
            timespec="seconds"
        )

    def mark_completed(
        self,
        result: Any = None,
    ) -> None:
        """
        Mark execution as completed.
        """

        self.status = ExecutionStatus.COMPLETED

        self.outcome = ExecutionOutcome.SUCCESS

        self.success = True

        self.result = result

        self.completed_at = datetime.now(
            timezone.utc
        ).isoformat(
            timespec="seconds"
        )

        self.duration = self.elapsed_time()

    def mark_failed(
        self,
        error: DARFExecutionError,
    ) -> None:
        """
        Mark execution as failed.
        """

        self.status = ExecutionStatus.FAILED

        self.outcome = ExecutionOutcome.FAILURE

        self.success = False

        self.error = error

        self.completed_at = datetime.now(
            timezone.utc
        ).isoformat(
            timespec="seconds"
        )

        self.duration = self.elapsed_time()

    def mark_cancelled(
        self,
    ) -> None:
        """
        Mark execution as cancelled.
        """

        self.status = ExecutionStatus.CANCELLED

        self.outcome = ExecutionOutcome.CANCELLED

        self.success = False

        self.completed_at = datetime.now(
            timezone.utc
        ).isoformat(
            timespec="seconds"
        )

        self.duration = self.elapsed_time()

    # ========================================================
    # METRICS
    # ========================================================

    def add_metric(
        self,
        name: str,
        value: float,
    ) -> None:
        """
        Add execution metric.
        """

        self.metrics[name] = value

    def add_warning(
        self,
        warning: str,
    ) -> None:
        """
        Record execution warning.
        """

        self.warnings.append(
            warning
        )

    # ========================================================
    # TIMING
    # ========================================================

    def elapsed_time(
        self,
    ) -> Optional[float]:
        """
        Calculate execution duration
        in seconds.
        """

        if self.started_at is None:
            return None

        end_time = (
            self.completed_at
            if self.completed_at
            else datetime.now(
                timezone.utc
            ).isoformat(
                timespec="seconds"
            )
        )

        start = datetime.fromisoformat(
            self.started_at
        )

        end = datetime.fromisoformat(
            end_time
        )

        return round(
            (
                end - start
            ).total_seconds(),
            6,
        )
        # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert execution result
        into a dictionary.
        """

        return {
            "execution_id": self.execution_id,
            "request_id": self.request_id,
            "agent_id": self.agent_id,
            "task_name": self.task_name,
            "status": self.status.value,
            "outcome": self.outcome.value,
            "success": self.success,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration": self.duration,
            "result": self.result,
            "metadata": self.metadata,
            "metrics": self.metrics,
            "warnings": self.warnings,
            "error": (
                self.error.to_dict()
                if self.error
                else None
            ),
            "version": self.version,
        }

    def to_json(
        self,
    ) -> str:
        """
        Convert execution result
        into JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=4,
            sort_keys=True,
        )

    # ========================================================
    # FACTORY
    # ========================================================

    @classmethod
    def from_exception(
        cls,
        error: DARFExecutionError,
    ) -> "ExecutionResult":
        """
        Build a failed execution result
        directly from an exception.
        """

        result = cls()

        result.mark_failed(error)

        return result

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(
        self,
    ) -> str:

        return (
            f"[{self.status.value}] "
            f"{self.execution_id}"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<ExecutionResult "
            f"id='{self.execution_id}' "
            f"status='{self.status.value}' "
            f"success={self.success}>"
        )