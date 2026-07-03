"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Execution History

Purpose
-------
Defines the execution history module used by the
DARF Execution Fabric.

Responsibilities
----------------
- Track task execution status
- Compute execution statistics
- Provide execution timeline

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

__all__ = [
    "ExecutionRecord",
    "ExecutionHistory",
]

# ============================================================
# EXECUTION RECORD
# ============================================================

@dataclass(slots=True)
class ExecutionRecord:
    """
    Represents one completed (or running)
    execution of a task.
    """

    record_id: str = field(
        default_factory=lambda: f"EXECHIST-{uuid.uuid4().hex.upper()}"
    )
    task_id: str = ""
    task_name: str = ""
    success: bool = False
    status: str = "created"
    started_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    finished_at: Optional[str] = None
    duration: float = 0.0
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    def __post_init__(self) -> None:
        if not self.task_id:
            raise ValueError("task_id cannot be empty.")


# ============================================================
# EXECUTION HISTORY
# ============================================================

@dataclass(slots=True)
class ExecutionHistory:
    """
    Chronological execution history.
    """

    records: List[ExecutionRecord] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    def __post_init__(self) -> None:
        if self.records is None:
            raise ValueError("records cannot be None.")

    # ============================================================
    # RECORD MANAGEMENT
    # ============================================================

    def add(self, record: ExecutionRecord) -> None:
        """
        Add an execution record.
        """
        if not isinstance(record, ExecutionRecord):
            raise TypeError("record must be an ExecutionRecord.")

        if self.contains(record.task_id):
            raise ValueError(f"Task '{record.task_id}' already exists.")

        self.records.append(record)

    def get(self, task_id: str) -> Optional[ExecutionRecord]:
        """
        Return a record by task ID.
        """
        for record in self.records:
            if record.task_id == task_id:
                return record
        return None

    def contains(self, task_id: str) -> bool:
        """
        Determine whether a task record exists.
        """
        return self.get(task_id) is not None

    def last(self) -> Optional[ExecutionRecord]:
        """
        Return the most recent record.
        """
        if self.is_empty():
            return None
        return self.records[-1]

    def remove(self, task_id: str) -> bool:
        """
        Remove a record by task ID.
        """
        record = self.get(task_id)
        if record is None:
            return False

        self.records.remove(record)
        return True

    def clear(self) -> None:
        """
        Remove every execution record.
        """
        self.records.clear()

    def count(self) -> int:
        """
        Return total number of records.
        """
        return len(self.records)

    def is_empty(self) -> bool:
        """
        Determine whether the history is empty.
        """
        return self.count() == 0

    # ============================================================
    # RECORD FILTERS
    # ============================================================

    def successful(self) -> List[ExecutionRecord]:
        """
        Return all successful execution records.
        """
        return [record for record in self.records if record.success]

    def failed(self) -> List[ExecutionRecord]:
        """
        Return all failed execution records.
        """
        return [record for record in self.records if not record.success]

    def running(self) -> List[ExecutionRecord]:
        """
        Return all running execution records.
        """
        return [record for record in self.records if record.status.lower() == "running"]

    def completed(self) -> List[ExecutionRecord]:
        """
        Return all completed execution records.
        """
        return [record for record in self.records if record.status.lower() == "completed"]

    def pending(self) -> List[ExecutionRecord]:
        """
        Return all pending execution records.
        """
        return [record for record in self.records if record.status.lower() in ("created", "pending")]

    # ============================================================
    # STATISTICS
    # ============================================================

    def success_count(self) -> int:
        """
        Return the number of successful executions.
        """
        return len(self.successful())

    def failure_count(self) -> int:
        """
        Return the number of failed executions.
        """
        return len(self.failed())

    def running_count(self) -> int:
        """
        Return the number of running executions.
        """
        return len(self.running())

    def completed_count(self) -> int:
        """
        Return the number of completed executions.
        """
        return len(self.completed())

    def pending_count(self) -> int:
        """
        Return the number of pending executions.
        """
        return len(self.pending())

    def success_rate(self) -> float:
        """
        Return execution success rate.
        """
        total = self.count()
        if total == 0:
            return 0.0
        return self.success_count() / total

    def failure_rate(self) -> float:
        """
        Return execution failure rate.
        """
        total = self.count()
        if total == 0:
            return 0.0
        return self.failure_count() / total

    def average_duration(self) -> float:
        """
        Return average execution duration.
        """
        if self.is_empty():
            return 0.0
        return sum(record.duration for record in self.records) / self.count()

    def total_duration(self) -> float:
        """
        Return cumulative execution time.
        """
        return sum(record.duration for record in self.records)

    # ============================================================
    # SERIALIZATION
    # ============================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize execution history.
        """
        return {
            "count": self.count(),
            "success_count": self.success_count(),
            "failure_count": self.failure_count(),
            "running_count": self.running_count(),
            "completed_count": self.completed_count(),
            "pending_count": self.pending_count(),
            "success_rate": self.success_rate(),
            "failure_rate": self.failure_rate(),
            "average_duration": self.average_duration(),
            "total_duration": self.total_duration(),
            "records": [
                {
                    "record_id": record.record_id,
                    "task_id": record.task_id,
                    "task_name": record.task_name,
                    "success": record.success,
                    "status": record.status,
                    "started_at": record.started_at,
                    "finished_at": record.finished_at,
                    "duration": record.duration,
                    "output": record.output,
                    "error": record.error,
                    "metadata": record.metadata,
                    "version": record.version,
                }
                for record in self.records
            ],
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """
        Serialize execution history to JSON.
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
        Return total number of records.
        """
        return self.count()

    def __iter__(self):
        """
        Iterate over execution records.
        """
        return iter(self.records)

    def __contains__(self, task_id: str) -> bool:
        """
        Determine whether a task exists in the execution history.
        """
        return self.contains(task_id)

    # ============================================================
    # REPRESENTATION
    # ============================================================

    def __str__(self) -> str:
        """
        Human-readable representation.
        """
        return f"ExecutionHistory({self.count()} records)"

    def __repr__(self) -> str:
        """
        Developer representation.
        """
        return (
            f"<ExecutionHistory "
            f"records={self.count()} "
            f"success={self.success_count()} "
            f"failed={self.failure_count()}>"
        )