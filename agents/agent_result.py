"""
Distributed Agentic Reasoning Framework (DARF)
Agent Runtime

Agent Result

Purpose
-------
Defines the canonical execution result produced by
DARF agents.

Responsibilities
----------------
- Agent execution outcome
- Execution timing
- Result storage
- Error reporting
- Serialization

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

from datetime import datetime
from datetime import timezone

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

__all__ = [
    "AgentResult",
]
# ============================================================
# AGENT RESULT
# ============================================================


@dataclass(slots=True)
class AgentResult:
    """
    Canonical agent execution result.
    """

    result_id: str = field(
        default_factory=lambda: (
            f"AGENTRES-{uuid.uuid4().hex.upper()}"
        )
    )

    agent_id: Optional[str] = None

    task_id: Optional[str] = None

    success: bool = False

    output: Any = None

    error: Optional[str] = None

    created_at: str = field(
        default_factory=lambda: (
            datetime.now(
                timezone.utc
            ).isoformat(timespec="seconds")
        )
    )

    duration: float = 0.0

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    warnings: List[
        str
    ] = field(
        default_factory=list
    )

    version: str = "1.0"

    _start_time: float = field(
        init=False,
        repr=False,
    )

    def __post_init__(
        self,
    ) -> None:

        self._start_time = time.perf_counter()

    # ========================================================
    # STATE
    # ========================================================

    def mark_success(
        self,
        output: Any = None,
    ) -> None:

        self.success = True

        self.output = output

        self.duration = (
            time.perf_counter()
            - self._start_time
        )

    def mark_failure(
        self,
        error: str,
    ) -> None:

        self.success = False

        self.error = error

        self.duration = (
            time.perf_counter()
            - self._start_time
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def add_warning(
        self,
        warning: str,
    ) -> None:

        self.warnings.append(
            warning
        )

    def has_warnings(
        self,
    ) -> bool:

        return bool(
            self.warnings
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
            "result_id": self.result_id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "created_at": self.created_at,
            "duration": self.duration,
            "warnings": self.warnings,
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
            default=str,
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
            f"({self.duration:.4f}s)"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<AgentResult "
            f"id='{self.result_id}' "
            f"success={self.success}>"
        )