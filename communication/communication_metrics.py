"""
Distributed Agentic Reasoning Framework (DARF)

Communication Metrics

Tracks message traffic across the framework.
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict


@dataclass(slots=True)
class CommunicationMetrics:

    sent: int = 0

    received: int = 0

    routed: int = 0

    broadcasts: int = 0

    failed: int = 0

    dropped: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # Record Operations
    # ---------------------------------------------------------

    def record_sent(self) -> None:

        self.sent += 1

    def record_received(self) -> None:

        self.received += 1

    def record_routed(self) -> None:

        self.routed += 1

    def record_broadcast(self) -> None:

        self.broadcasts += 1

    def record_failed(self) -> None:

        self.failed += 1

    def record_dropped(self) -> None:

        self.dropped += 1

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def total_messages(self) -> int:

        return self.sent + self.received

    def success_rate(self) -> float:

        if self.sent == 0:

            return 0.0

        successful = self.sent - self.failed

        return successful / self.sent

    def reset(self) -> None:

        self.sent = 0

        self.received = 0

        self.routed = 0

        self.broadcasts = 0

        self.failed = 0

        self.dropped = 0

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:

        return {

            "sent": self.sent,

            "received": self.received,

            "routed": self.routed,

            "broadcasts": self.broadcasts,

            "failed": self.failed,

            "dropped": self.dropped,

            "total_messages": self.total_messages(),

            "success_rate": self.success_rate(),

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

            f"CommunicationMetrics(sent={self.sent}, "

            f"received={self.received})"

        )

    def __repr__(self) -> str:

        return (

            "<CommunicationMetrics "

            f"messages={self.total_messages()}>"

        )