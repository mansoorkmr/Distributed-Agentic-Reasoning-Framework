"""
Distributed Agentic Reasoning Framework (DARF)

Runtime Metrics

Tracks runtime activity and health.
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict


@dataclass(slots=True)
class RuntimeMetrics:

    startups: int = 0

    shutdowns: int = 0

    requests: int = 0

    failures: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # Recording
    # ---------------------------------------------------------

    def record_startup(self) -> None:

        self.startups += 1

    def record_shutdown(self) -> None:

        self.shutdowns += 1

    def record_request(self) -> None:

        self.requests += 1

    def record_failure(self) -> None:

        self.failures += 1

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def success_count(self) -> int:

        return max(
            0,
            self.requests - self.failures,
        )

    def success_rate(self) -> float:

        if self.requests == 0:

            return 0.0

        return self.success_count() / self.requests

    def failure_rate(self) -> float:

        if self.requests == 0:

            return 0.0

        return self.failures / self.requests

    def reset(self) -> None:

        self.startups = 0

        self.shutdowns = 0

        self.requests = 0

        self.failures = 0

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:

        return {

            "startups": self.startups,

            "shutdowns": self.shutdowns,

            "requests": self.requests,

            "failures": self.failures,

            "success_count": self.success_count(),

            "success_rate": self.success_rate(),

            "failure_rate": self.failure_rate(),

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(self) -> str:

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(self) -> str:

        return (

            f"RuntimeMetrics(requests={self.requests})"

        )

    def __repr__(self) -> str:

        return (

            "<RuntimeMetrics "

            f"requests={self.requests}>"

        )