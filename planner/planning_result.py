"""
Distributed Agentic Reasoning Framework (DARF)
Planner

Planning Result

Purpose
-------
Defines the canonical planning result produced
by the DARF Planner.

A planning result represents the outcome of the
planning stage and encapsulates the generated
execution plan together with planning metadata.

Responsibilities
----------------
- Planning outcome
- Execution plan storage
- Planning duration
- Warning collection
- Error collection
- Serialization

Design Principles
-----------------
- Immutable planning contract
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
import time
import uuid

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from execution.execution_plan import ExecutionPlan

__all__ = [
    "PlanningResult",
]
# ============================================================
# PLANNING RESULT
# ============================================================


@dataclass(slots=True)
class PlanningResult:
    """
    Canonical planning result.
    """

    planning_id: str = field(
        default_factory=lambda: (
            f"PLANRES-{uuid.uuid4().hex.upper()}"
        )
    )

    request_id: Optional[str] = None

    success: bool = False

    execution_plan: Optional[
        ExecutionPlan
    ] = None

    created_at: float = field(
        default_factory=time.perf_counter
    )

    planning_time: float = 0.0

    warnings: List[
        str
    ] = field(
        default_factory=list
    )

    error: Optional[str] = None

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
        # ========================================================
    # VALIDATION
    # ========================================================

    def __post_init__(
        self,
    ) -> None:

        if self.planning_time < 0:

            raise ValueError(
                "planning_time must be >= 0."
            )
            # ========================================================
    # STATE
    # ========================================================

    def mark_success(
        self,
        plan: ExecutionPlan,
    ) -> None:
        """
        Mark planning as successful.
        """

        self.success = True
        self.execution_plan = plan
        self.planning_time = (
            time.perf_counter()
            - self.created_at
        )

    def mark_failure(
        self,
        error: str,
    ) -> None:
        """
        Mark planning as failed.
        """

        self.success = False
        self.error = error
        self.planning_time = (
            time.perf_counter()
            - self.created_at
        )
            # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {
            "planning_id": self.planning_id,
            "request_id": self.request_id,
            "success": self.success,
            "planning_time": self.planning_time,
            "execution_plan": (
                self.execution_plan.to_dict()
                if self.execution_plan
                else None
            ),
            "warnings": self.warnings,
            "error": self.error,
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

        status = (
            "success"
            if self.success
            else "failed"
        )

        return (
            f"{status} "
            f"({self.planning_time:.4f}s)"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<PlanningResult "
            f"id='{self.planning_id}' "
            f"success={self.success}>"
        )