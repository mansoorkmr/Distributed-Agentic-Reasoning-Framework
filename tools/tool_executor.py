"""
Distributed Agentic Reasoning Framework (DARF)

Tool Executor
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any

from tools.tool import Tool
from tools.tool_result import ToolResult


@dataclass(slots=True)
class ToolExecutor:

    executions: int = 0

    metadata: dict = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------

    def execute(
        self,
        tool: Tool,
        *args,
        **kwargs,
    ) -> ToolResult:

        result = ToolResult()

        result.tool_id = tool.tool_id

        self.executions += 1

        try:

            output = tool.execute(
                *args,
                **kwargs,
            )

            result.mark_success(
                output=output,
            )

        except Exception as exc:

            result.mark_failure(exc)

        return result

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def execution_count(
        self,
    ) -> int:

        return self.executions

    def reset(
        self,
    ) -> None:

        self.executions = 0

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(
        self,
    ):

        return {

            "executions": self.executions,

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(
        self,
    ):

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(
        self,
    ):

        return (

            f"ToolExecutor({self.executions} executions)"

        )

    def __repr__(
        self,
    ):

        return (

            "<ToolExecutor "

            f"executions={self.executions}>"

        )