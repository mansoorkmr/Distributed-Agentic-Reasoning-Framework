"""
Distributed Agentic Reasoning Framework (DARF)

Tool Result
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
from typing import Optional


def _result_id() -> str:

    return f"TOOLRES-{uuid.uuid4().hex.upper()}"


@dataclass(slots=True)
class ToolResult:

    result_id: str = field(
        default_factory=_result_id
    )

    tool_id: Optional[str] = None

    success: bool = False

    output: Any = None

    error: Optional[str] = None

    created_at: str = field(

        default_factory=lambda:

        datetime.now(
            timezone.utc
        ).isoformat()

    )

    duration: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"

    _start_time: float = field(

        default_factory=time.perf_counter,

        init=False,

        repr=False,

    )

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    def mark_success(

        self,

        output: Any = None,

    ) -> None:

        self.success = True

        self.output = output

        self.error = None

        self.duration = (

            time.perf_counter()

            - self._start_time

        )

    def mark_failure(

        self,

        error: Exception | str,

    ) -> None:

        self.success = False

        self.output = None

        self.error = str(error)

        self.duration = (

            time.perf_counter()

            - self._start_time

        )

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "result_id": self.result_id,

            "tool_id": self.tool_id,

            "success": self.success,

            "output": self.output,

            "error": self.error,

            "created_at": self.created_at,

            "duration": self.duration,

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(self):

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

            default=str,

        )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(self):

        if self.success:

            return (

                f"success "

                f"({self.duration:.4f}s)"

            )

        return (

            f"failed "

            f"({self.duration:.4f}s)"

        )

    def __repr__(self):

        return (

            "<ToolResult "

            f"id='{self.result_id}' "

            f"success={self.success}>"

        )