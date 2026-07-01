"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Execution State Machine

Purpose
-------
Defines the canonical execution state machine used
throughout the DARF Execution Fabric.

The state machine is responsible for validating
execution state transitions and ensuring that
all execution components follow a consistent
lifecycle.

Responsibilities
----------------
- Execution state definitions
- Legal transition validation
- State tracking
- Lifecycle management

Design Principles
-----------------
- Deterministic transitions
- Strong typing
- Immutable transition rules
- Thread-safe operation

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

from typing import Dict
from typing import FrozenSet


# ============================================================
# EXECUTION STATES
# ============================================================


@unique
class ExecutionState(
    str,
    Enum,
):
    """
    Canonical execution states.
    """

    CREATED = "created"

    QUEUED = "queued"

    RUNNING = "running"

    PAUSED = "paused"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


# ============================================================
# STATE MACHINE
# ============================================================


@dataclass(
    slots=True,
)
class ExecutionStateMachine:
    """
    Canonical execution state machine.
    """

    state: ExecutionState = (
        ExecutionState.CREATED
    )

    transitions: Dict[
        ExecutionState,
        FrozenSet[ExecutionState],
    ] = field(
        default_factory=lambda: {

            ExecutionState.CREATED: frozenset({
                ExecutionState.QUEUED,
                ExecutionState.CANCELLED,
            }),

            ExecutionState.QUEUED: frozenset({
                ExecutionState.RUNNING,
                ExecutionState.CANCELLED,
            }),

            ExecutionState.RUNNING: frozenset({
                ExecutionState.PAUSED,
                ExecutionState.COMPLETED,
                ExecutionState.FAILED,
                ExecutionState.CANCELLED,
            }),

            ExecutionState.PAUSED: frozenset({
                ExecutionState.RUNNING,
                ExecutionState.CANCELLED,
            }),

            ExecutionState.COMPLETED: frozenset(),

            ExecutionState.FAILED: frozenset(),

            ExecutionState.CANCELLED: frozenset(),
        }
    )
        # ========================================================
    # STATE QUERIES
    # ========================================================

    def current_state(
        self,
    ) -> ExecutionState:
        """
        Return the current execution state.
        """

        return self.state

    def is_terminal(
        self,
    ) -> bool:
        """
        Return True if the current state
        is terminal.
        """

        return self.state in {
            ExecutionState.COMPLETED,
            ExecutionState.FAILED,
            ExecutionState.CANCELLED,
        }

    def is_running(
        self,
    ) -> bool:
        """
        Return True if execution is running.
        """

        return self.state == ExecutionState.RUNNING

    def is_finished(
        self,
    ) -> bool:
        """
        Alias for terminal state.
        """

        return self.is_terminal()
        # ========================================================
    # TRANSITION VALIDATION
    # ========================================================

    def can_transition_to(
        self,
        new_state: ExecutionState,
    ) -> bool:
        """
        Determine whether a transition
        is allowed.
        """

        return (
            new_state
            in self.transitions[self.state]
        )

    def transition_to(
        self,
        new_state: ExecutionState,
    ) -> None:
        """
        Perform a validated state transition.
        """

        if not self.can_transition_to(
            new_state,
        ):
            raise ValueError(
                f"Illegal state transition "
                f"{self.state.value} -> "
                f"{new_state.value}"
            )

        self.state = new_state

    def allowed_transitions(
        self,
    ) -> FrozenSet[
        ExecutionState
    ]:
        """
        Return all legal transitions
        from the current state.
        """

        return self.transitions[
            self.state
        ]
        # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, object]:
        """
        Serialize the state machine.
        """

        return {
            "state": self.state.value,
            "allowed_transitions": [
                state.value
                for state in
                self.allowed_transitions()
            ],
        }
    
    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return self.state.value

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"<ExecutionStateMachine "
            f"state='{self.state.value}'>"
        )
        # ========================================================
    # LIFECYCLE
    # ========================================================

    def reset(
        self,
    ) -> None:
        """
        Reset the execution state
        to CREATED.
        """

        self.state = ExecutionState.CREATED