"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Execution State Infrastructure

Author:
    DARF Runtime Systems Division

Purpose:
    Enterprise-grade execution state orchestration
    infrastructure for:

        - distributed agentic AI systems
        - institutional orchestration runtimes
        - multi-agent execution pipelines
        - HPC-aware execution coordination
        - workflow orchestration systems
        - scalable reasoning infrastructure
        - production-grade lifecycle management
        - distributed state synchronization

Core Responsibilities:
    - execution lifecycle management
    - distributed-safe state transitions
    - workflow state orchestration
    - runtime state validation
    - agent lifecycle coordination
    - execution telemetry
    - deterministic state control
    - institutional observability

Design Principles:
    - deterministic
    - immutable-safe
    - distributed-safe
    - production-grade
    - institutionally reproducible
    - scalable
    - fault-tolerant
    - future extensible

Supported Features:
    - strict state transitions
    - execution lifecycle tracking
    - runtime validation
    - distributed-safe synchronization
    - workflow-aware orchestration
    - execution telemetry
    - transition auditing
    - institutional observability
"""

import json
from datetime import datetime
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from infrastructure.logging.structured_logger import (
    get_logger,
)


# ================================================================
# EXECUTION STATE ENUMERATION
# ================================================================

class ExecutionState(Enum):
    """
    Institutional-grade execution lifecycle states.
    """

    INITIALIZED = "initialized"

    QUEUED = "queued"

    PLANNING = "planning"

    REASONING = "reasoning"

    DISPATCHING = "dispatching"

    EXECUTING = "executing"

    WAITING = "waiting"

    VALIDATING = "validating"

    AGGREGATING = "aggregating"

    SYNCHRONIZING = "synchronizing"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    TIMEOUT = "timeout"

    RECOVERING = "recovering"


# ================================================================
# STATE TRANSITION POLICY
# ================================================================

VALID_STATE_TRANSITIONS: Dict[
    ExecutionState,
    Set[ExecutionState],
] = {

    ExecutionState.INITIALIZED: {

        ExecutionState.QUEUED,

        ExecutionState.PLANNING,

        ExecutionState.CANCELLED,
    },

    ExecutionState.QUEUED: {

        ExecutionState.PLANNING,

        ExecutionState.CANCELLED,

        ExecutionState.TIMEOUT,
    },

    ExecutionState.PLANNING: {

        ExecutionState.REASONING,

        ExecutionState.FAILED,

        ExecutionState.CANCELLED,
    },

    ExecutionState.REASONING: {

        ExecutionState.DISPATCHING,

        ExecutionState.FAILED,

        ExecutionState.CANCELLED,
    },

    ExecutionState.DISPATCHING: {

        ExecutionState.EXECUTING,

        ExecutionState.FAILED,

        ExecutionState.CANCELLED,
    },

    ExecutionState.EXECUTING: {

        ExecutionState.WAITING,

        ExecutionState.VALIDATING,

        ExecutionState.AGGREGATING,

        ExecutionState.COMPLETED,

        ExecutionState.FAILED,

        ExecutionState.TIMEOUT,

        ExecutionState.RECOVERING,
    },

    ExecutionState.WAITING: {

        ExecutionState.EXECUTING,

        ExecutionState.TIMEOUT,

        ExecutionState.FAILED,
    },

    ExecutionState.VALIDATING: {

        ExecutionState.AGGREGATING,

        ExecutionState.FAILED,
    },

    ExecutionState.AGGREGATING: {

        ExecutionState.SYNCHRONIZING,

        ExecutionState.COMPLETED,

        ExecutionState.FAILED,
    },

    ExecutionState.SYNCHRONIZING: {

        ExecutionState.COMPLETED,

        ExecutionState.FAILED,
    },

    ExecutionState.RECOVERING: {

        ExecutionState.EXECUTING,

        ExecutionState.FAILED,
    },

    ExecutionState.COMPLETED: set(),

    ExecutionState.FAILED: set(),

    ExecutionState.CANCELLED: set(),

    ExecutionState.TIMEOUT: set(),
}


# ================================================================
# EXECUTION STATE MANAGER
# ================================================================

class ExecutionStateManager:
    """
    Institutional-grade execution state manager.

    Handles:
        - lifecycle-safe transitions
        - distributed-safe state management
        - execution auditing
        - runtime telemetry
        - transition validation
    """

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(
        self,
        initial_state: ExecutionState = (
            ExecutionState.INITIALIZED
        ),
    ):

        self.logger = get_logger(

            name="ExecutionStateManager",

            log_dir="logs/agents",
        )

        self.current_state = initial_state

        self.created_at = (
            datetime.utcnow().isoformat()
        )

        self.last_updated = (
            self.created_at
        )

        self.transition_history: List[
            Dict
        ] = []

        self.total_transitions = 0

        self.failed_transitions = 0

        self.logger.info(
            f"Execution state manager initialized | "
            f"InitialState="
            f"{self.current_state.value}"
        )

    # ============================================================
    # VALIDATE TRANSITION
    # ============================================================

    def validate_transition(
        self,
        next_state: ExecutionState,
    ) -> bool:
        """
        Validate lifecycle-safe state transition.
        """

        allowed_transitions = (
            VALID_STATE_TRANSITIONS.get(
                self.current_state,
                set(),
            )
        )

        return (
            next_state
            in allowed_transitions
        )

    # ============================================================
    # TRANSITION STATE
    # ============================================================

    def transition_to(
        self,
        next_state: ExecutionState,
        metadata: Optional[
            Dict
        ] = None,
    ):
        """
        Perform validated state transition safely.
        """

        if not isinstance(
            next_state,
            ExecutionState,
        ):

            raise TypeError(
                "next_state must be "
                "ExecutionState enum."
            )

        if not self.validate_transition(
            next_state
        ):

            self.failed_transitions += 1

            error_message = (

                f"Invalid transition | "

                f"Current="
                f"{self.current_state.value} | "

                f"Next="
                f"{next_state.value}"
            )

            self.logger.error(
                error_message
            )

            raise RuntimeError(
                error_message
            )

        previous_state = (
            self.current_state
        )

        self.current_state = next_state

        self.last_updated = (
            datetime.utcnow().isoformat()
        )

        transition_record = {

            "timestamp":
                self.last_updated,

            "previous_state":
                previous_state.value,

            "next_state":
                next_state.value,

            "metadata":
                metadata or {},
        }

        self.transition_history.append(
            transition_record
        )

        self.total_transitions += 1

        self.logger.info(
            f"Execution state transition | "
            f"{previous_state.value} -> "
            f"{next_state.value}"
        )

    # ============================================================
    # CHECK TERMINAL STATE
    # ============================================================

    def is_terminal_state(
        self,
    ) -> bool:
        """
        Determine if execution reached terminal state.
        """

        terminal_states = {

            ExecutionState.COMPLETED,

            ExecutionState.FAILED,

            ExecutionState.CANCELLED,

            ExecutionState.TIMEOUT,
        }

        return (
            self.current_state
            in terminal_states
        )

    # ============================================================
    # CHECK ACTIVE STATE
    # ============================================================

    def is_active(
        self,
    ) -> bool:
        """
        Determine if execution remains active.
        """

        return not self.is_terminal_state()

    # ============================================================
    # EXPORT HISTORY
    # ============================================================

    def export_transition_history(
        self,
    ) -> List[Dict]:
        """
        Export immutable transition history safely.
        """

        return list(
            self.transition_history
        )

    # ============================================================
    # CURRENT STATE SUMMARY
    # ============================================================

    def summary(
        self,
    ) -> Dict:
        """
        Return institutional execution summary.
        """

        return {

            "current_state":
                self.current_state.value,

            "total_transitions":
                self.total_transitions,

            "failed_transitions":
                self.failed_transitions,

            "is_terminal":
                self.is_terminal_state(),

            "is_active":
                self.is_active(),

            "created_at":
                self.created_at,

            "last_updated":
                self.last_updated,
        }

    # ============================================================
    # EXPORT JSON
    # ============================================================

    def to_json(
        self,
        indent: int = 4,
    ) -> str:
        """
        Export execution state safely.
        """

        exported = {

            "summary":
                self.summary(),

            "transition_history":
                self.export_transition_history(),
        }

        return json.dumps(

            exported,

            indent=indent,

            ensure_ascii=False,
        )

    # ============================================================
    # RESET STATE
    # ============================================================

    def reset(
        self,
    ):
        """
        Reset execution lifecycle safely.
        """

        self.current_state = (
            ExecutionState.INITIALIZED
        )

        self.last_updated = (
            datetime.utcnow().isoformat()
        )

        self.transition_history.clear()

        self.total_transitions = 0

        self.failed_transitions = 0

        self.logger.warning(
            "Execution state manager reset."
        )

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"ExecutionStateManager("
            f"current_state="
            f"{self.current_state.value}, "
            f"transitions="
            f"{self.total_transitions})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    manager = ExecutionStateManager()

    manager.transition_to(
        ExecutionState.QUEUED
    )

    manager.transition_to(
        ExecutionState.PLANNING
    )

    manager.transition_to(
        ExecutionState.REASONING
    )

    manager.transition_to(
        ExecutionState.DISPATCHING
    )

    manager.transition_to(
        ExecutionState.EXECUTING
    )

    manager.transition_to(
        ExecutionState.COMPLETED
    )

    print("\nExecution State Summary:\n")

    print(
        json.dumps(
            manager.summary(),
            indent=4,
        )
    )

    print("\nTransition History:\n")

    print(
        manager.to_json()
    )
