"""
Distributed Agentic Reasoning Framework (DARF)

Tool Metrics
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class ToolMetrics:

    executions: int = 0

    successes: int = 0

    failures: int = 0

    retries: int = 0

    timeouts: int = 0

    total_execution_time: float = 0.0

    metadata: dict = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # Recording
    # ---------------------------------------------------------

    def record_success(
        self,
        duration: float = 0.0,
    ) -> None:

        self.executions += 1
        self.successes += 1
        self.total_execution_time += duration

    def record_failure(
        self,
        duration: float = 0.0,
    ) -> None:

        self.executions += 1
        self.failures += 1
        self.total_execution_time += duration

    def record_retry(self) -> None:

        self.retries += 1

    def record_timeout(self) -> None:

        self.timeouts += 1

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def success_rate(self) -> float:

        if self.executions == 0:
            return 0.0

        return self.successes / self.executions

    def failure_rate(self) -> float:

        if self.executions == 0:
            return 0.0

        return self.failures / self.executions

    def average_execution_time(self) -> float:

        if self.executions == 0:
            return 0.0

        return self.total_execution_time / self.executions

    def reset(self) -> None:

        self.executions = 0
        self.successes = 0
        self.failures = 0
        self.retries = 0
        self.timeouts = 0
        self.total_execution_time = 0.0

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "executions": self.executions,

            "successes": self.successes,

            "failures": self.failures,

            "retries": self.retries,

            "timeouts": self.timeouts,

            "average_execution_time":
                self.average_execution_time(),

            "success_rate":
                self.success_rate(),

            "failure_rate":
                self.failure_rate(),

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(self):

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(self):

        return (

            f"ToolMetrics(executions={self.executions})"

        )

    def __repr__(self):

        return (

            "<ToolMetrics "

            f"executions={self.executions}>"

        )