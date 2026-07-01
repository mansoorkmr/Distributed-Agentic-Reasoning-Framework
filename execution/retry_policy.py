"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Retry Policy

Purpose
-------
Defines the institutional retry policy used by the
DARF Execution Fabric.

The retry policy determines whether a failed execution
should be retried, when it should be retried, and how
retry delays are calculated.

Responsibilities
----------------
- Retry eligibility
- Retry strategies
- Delay calculation
- Backoff policies
- Retry accounting
- Future distributed execution support

Design Principles
-----------------
- Strong typing
- Deterministic behavior
- Extensible retry strategies
- Cloud-native execution support
- Production-ready serialization

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from enum import Enum
from enum import unique

import json
import random

from typing import Any
from typing import Dict
from typing import Optional
from typing import Type

from execution.exceptions import DARFExecutionError


# ============================================================
# RETRY STRATEGY
# ============================================================


@unique
class RetryStrategy(
    str,
    Enum,
):
    """
    Retry backoff strategy.
    """

    NO_RETRY = "no_retry"

    FIXED_DELAY = "fixed_delay"

    LINEAR_BACKOFF = "linear_backoff"

    EXPONENTIAL_BACKOFF = "exponential_backoff"

    EXPONENTIAL_WITH_JITTER = (
        "exponential_with_jitter"
    )


# ============================================================
# RETRY DECISION
# ============================================================


@unique
class RetryDecision(
    str,
    Enum,
):
    """
    Retry decision.
    """

    RETRY = "retry"

    FAIL = "fail"


# ============================================================
# RETRY POLICY
# ============================================================


@dataclass(
    slots=True,
)
class RetryPolicy:
    """
    Canonical retry policy for
    the DARF Execution Fabric.
    """

    max_attempts: int = 3

    initial_delay: float = 1.0

    maximum_delay: float = 30.0

    backoff_multiplier: float = 2.0

    retry_strategy: RetryStrategy = (
        RetryStrategy.EXPONENTIAL_BACKOFF
    )

    retry_timeout: Optional[
        float
    ] = None

    retryable_exceptions: tuple[
        Type[DARFExecutionError],
        ...
    ] = field(
        default_factory=lambda: (
            DARFExecutionError,
        )
    )

    attempt: int = 0

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
        Validate retry configuration.
        """

        if self.max_attempts < 0:
            raise ValueError(
                "max_attempts must be >= 0."
            )

        if self.initial_delay < 0:
            raise ValueError(
                "initial_delay must be >= 0."
            )

        if self.maximum_delay < 0:
            raise ValueError(
                "maximum_delay must be >= 0."
            )

        if (
            self.maximum_delay
            < self.initial_delay
        ):
            raise ValueError(
                "maximum_delay cannot be smaller "
                "than initial_delay."
            )

        if self.backoff_multiplier < 1.0:
            raise ValueError(
                "backoff_multiplier "
                "must be >= 1.0."
            )
        # ========================================================
    # RETRY DECISION
    # ========================================================

    def should_retry(
        self,
        error: Exception,
    ) -> bool:
        """
        Determine whether the given exception
        should be retried.
        """

        if self.retry_strategy == RetryStrategy.NO_RETRY:
            return False

        if self.attempt >= self.max_attempts:
            return False

        return isinstance(
            error,
            self.retryable_exceptions,
        )

    # ========================================================
    # ATTEMPT MANAGEMENT
    # ========================================================

    def register_attempt(
        self,
    ) -> None:
        """
        Register a retry attempt.
        """

        self.attempt += 1

    def reset(
        self,
    ) -> None:
        """
        Reset retry state.
        """

        self.attempt = 0

    # ========================================================
    # DELAY CALCULATION
    # ========================================================

    def compute_delay(
        self,
    ) -> float:
        """
        Compute retry delay according to the
        configured retry strategy.
        """

        if (
            self.retry_strategy
            == RetryStrategy.NO_RETRY
        ):
            return 0.0

        if (
            self.retry_strategy
            == RetryStrategy.FIXED_DELAY
        ):
            delay = self.initial_delay

        elif (
            self.retry_strategy
            == RetryStrategy.LINEAR_BACKOFF
        ):
            delay = (
                self.initial_delay
                * max(
                    1,
                    self.attempt,
                )
            )

        elif (
            self.retry_strategy
            == RetryStrategy.EXPONENTIAL_BACKOFF
        ):
            delay = (
                self.initial_delay
                * (
                    self.backoff_multiplier
                    ** max(
                        0,
                        self.attempt - 1,
                    )
                )
            )

        elif (
            self.retry_strategy
            == RetryStrategy.EXPONENTIAL_WITH_JITTER
        ):
          

            delay = (
                self.initial_delay
                * (
                    self.backoff_multiplier
                    ** max(
                        0,
                        self.attempt - 1,
                    )
                )
            )

            delay *= random.uniform(
                0.8,
                1.2,
            )

        else:
            delay = self.initial_delay

        return min(
            delay,
            self.maximum_delay,
        )
        # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Convert retry policy to a dictionary.
        """

        return {
            "max_attempts": self.max_attempts,
            "initial_delay": self.initial_delay,
            "maximum_delay": self.maximum_delay,
            "backoff_multiplier": self.backoff_multiplier,
            "retry_strategy": self.retry_strategy.value,
            "retry_timeout": self.retry_timeout,
            "retryable_exceptions": [
                exc.__name__
                for exc in self.retryable_exceptions
            ],
            "attempt": self.attempt,
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(
        self,
    ) -> str:
        """
        Convert retry policy to JSON.
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
            f"{self.retry_strategy.value}"
            f" ({self.attempt}/"
            f"{self.max_attempts})"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<RetryPolicy "
            f"strategy='{self.retry_strategy.value}' "
            f"attempt={self.attempt} "
            f"max_attempts={self.max_attempts}>"
        )