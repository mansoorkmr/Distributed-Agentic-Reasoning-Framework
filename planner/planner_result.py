"""
Distributed Agentic Reasoning Framework (DARF)

Planner Result
"""

from __future__ import annotations

import json
import uuid

from dataclasses import dataclass, field
from typing import Optional

from execution.execution_plan import ExecutionPlan


def _result_id() -> str:
    return f"PLANRES-{uuid.uuid4().hex.upper()}"


@dataclass(slots=True)
class PlannerResult:

    result_id: str = field(default_factory=_result_id)

    success: bool = False

    execution_plan: Optional[ExecutionPlan] = None

    error: Optional[str] = None

    metadata: dict = field(default_factory=dict)

    version: str = "1.0"

    def mark_success(
        self,
        plan: ExecutionPlan,
    ) -> None:

        self.success = True
        self.execution_plan = plan
        self.error = None

    def mark_failure(
        self,
        error: Exception | str,
    ) -> None:

        self.success = False
        self.execution_plan = None
        self.error = str(error)

    def to_dict(self):

        return {

            "result_id": self.result_id,

            "success": self.success,

            "execution_plan":

                str(self.execution_plan)

                if self.execution_plan

                else None,

            "error": self.error,

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(self):

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )

    def __str__(self):

        if self.success:
            return "PlannerResult(success)"

        return "PlannerResult(failed)"

    def __repr__(self):

        return (

            "<PlannerResult "

            f"success={self.success}>"

        )