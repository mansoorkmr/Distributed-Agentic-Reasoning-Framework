"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Timeout Policy

Purpose
-------
Defines the canonical timeout policy used by the
DARF Execution Fabric.

The timeout policy determines the maximum execution
time allowed for an execution before it is considered
timed out.

Responsibilities
----------------
- Execution timeout limits
- Timeout validation
- Timeout accounting
- Future distributed execution support

Design Principles
-----------------
- Strong typing
- Deterministic behavior
- Production-ready
- Cloud-native compatibility

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from enum import Enum
from enum import unique

from typing import Any
from typing import Dict
from typing import Optional


# ============================================================
# TIMEOUT STRATEGY
# ============================================================


@unique
class TimeoutStrategy(
    str,
    Enum,
):
    """
    Timeout handling strategy.
    """

    NONE = "none"

    CANCEL = "cancel"

    FORCE_CANCEL = "force_cancel"

    TERMINATE = "terminate"


# ============================================================
# TIMEOUT POLICY
# ============================================================


@dataclass(
    slots=True,
)
class TimeoutPolicy:
    """
    Canonical timeout policy.
    """

    timeout_seconds: float = 300.0

    strategy: TimeoutStrategy = (
        TimeoutStrategy.CANCEL
    )

    check_interval: float = 1.0

    grace_period: float = 5.0

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
        """
        Validate timeout configuration.
        """

        if self.timeout_seconds < 0:
            raise ValueError(
                "timeout_seconds must be >= 0."
            )

        if self.check_interval <= 0:
            raise ValueError(
                "check_interval must be > 0."
            )

        if self.grace_period < 0:
            raise ValueError(
                "grace_period must be >= 0."
            )
            # ========================================================
    # TIMEOUT STATE
    # ========================================================

    def is_timeout_enabled(
        self,
    ) -> bool:
        """
        Return True if timeout enforcement
        is enabled.
        """

        return (
            self.strategy
            != TimeoutStrategy.NONE
            and self.timeout_seconds > 0
        )

    # ========================================================
    # TIME CALCULATIONS
    # ========================================================

    def has_timed_out(
        self,
        elapsed_seconds: float,
    ) -> bool:
        """
        Determine whether the execution
        has exceeded the configured timeout.
        """

        if not self.is_timeout_enabled():
            return False

        return (
            elapsed_seconds
            >= self.timeout_seconds
        )

    def remaining_time(
        self,
        elapsed_seconds: float,
    ) -> Optional[float]:
        """
        Return remaining execution time.
        """

        if not self.is_timeout_enabled():
            return None

        remaining = (
            self.timeout_seconds
            - elapsed_seconds
        )

        return max(
            0.0,
            round(
                remaining,
                6,
            ),
        )
        # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert timeout policy into
        a dictionary.
        """

        return {
            "timeout_seconds": self.timeout_seconds,
            "strategy": self.strategy.value,
            "check_interval": self.check_interval,
            "grace_period": self.grace_period,
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(
        self,
    ) -> str:
        """
        Convert timeout policy into JSON.
        """

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

        return (
            f"{self.strategy.value} "
            f"({self.timeout_seconds}s)"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<TimeoutPolicy "
            f"strategy='{self.strategy.value}' "
            f"timeout={self.timeout_seconds}s>"
        )