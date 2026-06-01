"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Training State Management Infrastructure

Author:
    DARF Training Infrastructure Division

Purpose:
    Centralized finite-state lifecycle management system
    for distributed training, orchestration, checkpointing,
    recovery, evaluation, and fault-tolerant execution.

Core Responsibilities:
    - Deterministic training lifecycle management
    - State transition validation
    - Distributed-safe synchronization
    - Recovery-aware execution tracking
    - HPC-compatible lifecycle control
    - Failure-state propagation
    - Event-driven orchestration support

Design Principles:
    - Deterministic
    - Fault tolerant
    - Distributed-safe
    - Recovery-aware
    - Future extensible
    - Production-grade reliability

Why FSM (Finite State Machine)?
    Institutional systems NEVER rely on:
        - random booleans
        - ad-hoc status flags
        - implicit lifecycle transitions

    Instead:
        S_t ∈ State Space

    This guarantees:
        - valid transitions
        - recoverability
        - orchestration correctness
        - distributed consistency
"""

from enum import Enum
from datetime import datetime
from threading import Lock

from infrastructure.logging.structured_logger import get_logger


# ===================================================================
# TRAINING STATES
# ===================================================================

class TrainingState(Enum):
    """
    Canonical training lifecycle states.
    """

    INITIALIZING = "INITIALIZING"

    VALIDATING_ENVIRONMENT = "VALIDATING_ENVIRONMENT"

    LOADING_CONFIGURATION = "LOADING_CONFIGURATION"

    LOADING_DATASETS = "LOADING_DATASETS"

    PREPROCESSING = "PREPROCESSING"

    BUILDING_MODEL = "BUILDING_MODEL"

    INITIALIZING_DISTRIBUTED = "INITIALIZING_DISTRIBUTED"

    TRAINING = "TRAINING"

    VALIDATING = "VALIDATING"

    EVALUATING = "EVALUATING"

    CHECKPOINTING = "CHECKPOINTING"

    SYNCHRONIZING = "SYNCHRONIZING"

    RECOVERING = "RECOVERING"

    PAUSED = "PAUSED"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    TERMINATED = "TERMINATED"


# ===================================================================
# VALID TRANSITIONS
# ===================================================================

VALID_TRANSITIONS = {

    TrainingState.INITIALIZING: {

        TrainingState.VALIDATING_ENVIRONMENT,

        TrainingState.FAILED
    },

    TrainingState.VALIDATING_ENVIRONMENT: {

        TrainingState.LOADING_CONFIGURATION,

        TrainingState.FAILED
    },

    TrainingState.LOADING_CONFIGURATION: {

        TrainingState.LOADING_DATASETS,

        TrainingState.FAILED
    },

    TrainingState.LOADING_DATASETS: {

        TrainingState.PREPROCESSING,

        TrainingState.FAILED
    },

    TrainingState.PREPROCESSING: {

        TrainingState.BUILDING_MODEL,

        TrainingState.FAILED
    },

    TrainingState.BUILDING_MODEL: {

        TrainingState.INITIALIZING_DISTRIBUTED,

        TrainingState.TRAINING,

        TrainingState.FAILED
    },

    TrainingState.INITIALIZING_DISTRIBUTED: {

        TrainingState.TRAINING,

        TrainingState.FAILED
    },

    TrainingState.TRAINING: {

        TrainingState.VALIDATING,

        TrainingState.CHECKPOINTING,

        TrainingState.SYNCHRONIZING,

        TrainingState.PAUSED,

        TrainingState.RECOVERING,

        TrainingState.COMPLETED,

        TrainingState.FAILED
    },

    TrainingState.VALIDATING: {

        TrainingState.TRAINING,

        TrainingState.EVALUATING,

        TrainingState.CHECKPOINTING,

        TrainingState.FAILED
    },

    TrainingState.EVALUATING: {

        TrainingState.CHECKPOINTING,

        TrainingState.COMPLETED,

        TrainingState.FAILED
    },

    TrainingState.CHECKPOINTING: {

        TrainingState.TRAINING,

        TrainingState.VALIDATING,

        TrainingState.COMPLETED,

        TrainingState.FAILED
    },

    TrainingState.SYNCHRONIZING: {

        TrainingState.TRAINING,

        TrainingState.FAILED
    },

    TrainingState.RECOVERING: {

        TrainingState.TRAINING,

        TrainingState.FAILED,

        TrainingState.TERMINATED
    },

    TrainingState.PAUSED: {

        TrainingState.TRAINING,

        TrainingState.TERMINATED
    },

    TrainingState.COMPLETED: set(),

    TrainingState.FAILED: {

        TrainingState.RECOVERING,

        TrainingState.TERMINATED
    },

    TrainingState.TERMINATED: set()
}


# ===================================================================
# STATE MANAGER
# ===================================================================

class StateManager:
    """
    Institutional-grade lifecycle state manager.

    Features:
        - transition validation
        - state history tracking
        - distributed-safe synchronization
        - fault-aware lifecycle management
        - orchestration support
    """

    def __init__(self):

        self.logger = get_logger(
            name="StateManager",
            log_dir="logs/system"
        )

        self._lock = Lock()

        self.current_state = (
            TrainingState.INITIALIZING
        )

        self.previous_state = None

        self.state_history = []

        self.created_at = datetime.utcnow()

        self.last_transition = datetime.utcnow()

        self._record_state(
            self.current_state,
            reason="System initialization"
        )

    # ===============================================================
    # TRANSITION VALIDATION
    # ===============================================================

    def can_transition(
        self,
        next_state
    ):

        """
        Validate state transition legality.
        """

        allowed_states = VALID_TRANSITIONS.get(
            self.current_state,
            set()
        )

        return next_state in allowed_states

    # ===============================================================
    # STATE TRANSITION
    # ===============================================================

    def transition(
        self,
        next_state,
        reason=None
    ):

        """
        Transition safely between lifecycle states.
        """

        with self._lock:

            if not isinstance(
                next_state,
                TrainingState
            ):

                raise TypeError(
                    "next_state must be "
                    "TrainingState enum"
                )

            if not self.can_transition(next_state):

                error_message = (
                    f"Invalid state transition: "
                    f"{self.current_state.value} -> "
                    f"{next_state.value}"
                )

                self.logger.error(error_message)

                raise ValueError(error_message)

            self.previous_state = self.current_state

            self.current_state = next_state

            self.last_transition = (
                datetime.utcnow()
            )

            self._record_state(
                next_state,
                reason
            )

            self.logger.info(
                f"State Transition: "
                f"{self.previous_state.value} -> "
                f"{self.current_state.value}"
            )

    # ===============================================================
    # STATE RECORDING
    # ===============================================================

    def _record_state(
        self,
        state,
        reason=None
    ):

        """
        Persist state history.
        """

        entry = {

            "timestamp":
                datetime.utcnow().isoformat(),

            "state":
                state.value,

            "reason":
                reason
        }

        self.state_history.append(entry)

    # ===============================================================
    # FAILURE HANDLING
    # ===============================================================

    def mark_failed(
        self,
        reason=None
    ):

        """
        Force transition into FAILED state.
        """

        with self._lock:

            self.previous_state = (
                self.current_state
            )

            self.current_state = (
                TrainingState.FAILED
            )

            self._record_state(
                TrainingState.FAILED,
                reason
            )

            self.logger.critical(
                f"System entered FAILED state. "
                f"Reason: {reason}"
            )

    # ===============================================================
    # RECOVERY
    # ===============================================================

    def begin_recovery(
        self,
        reason=None
    ):

        """
        Begin recovery lifecycle.
        """

        if self.current_state not in {

            TrainingState.FAILED,

            TrainingState.PAUSED
        }:

            raise RuntimeError(
                "Recovery only allowed from "
                "FAILED or PAUSED states."
            )

        self.transition(
            TrainingState.RECOVERING,
            reason=reason
        )

    # ===============================================================
    # STATUS HELPERS
    # ===============================================================

    def is_training(self):

        return (
            self.current_state ==
            TrainingState.TRAINING
        )

    def is_failed(self):

        return (
            self.current_state ==
            TrainingState.FAILED
        )

    def is_completed(self):

        return (
            self.current_state ==
            TrainingState.COMPLETED
        )

    def is_terminal(self):

        return self.current_state in {

            TrainingState.COMPLETED,

            TrainingState.TERMINATED
        }

    # ===============================================================
    # STATE EXPORT
    # ===============================================================

    def export_state(self):

        """
        Export lifecycle snapshot.
        """

        return {

            "current_state":
                self.current_state.value,

            "previous_state":
                (
                    self.previous_state.value
                    if self.previous_state
                    else None
                ),

            "created_at":
                self.created_at.isoformat(),

            "last_transition":
                self.last_transition.isoformat(),

            "history":
                self.state_history
        }

    # ===============================================================
    # RESET
    # ===============================================================

    def reset(self):

        """
        Reset lifecycle manager safely.
        """

        with self._lock:

            self.previous_state = None

            self.current_state = (
                TrainingState.INITIALIZING
            )

            self.state_history = []

            self.created_at = datetime.utcnow()

            self.last_transition = datetime.utcnow()

            self._record_state(
                self.current_state,
                reason="Lifecycle reset"
            )

            self.logger.warning(
                "StateManager reset completed."
            )

    # ===============================================================
    # STRING REPRESENTATION
    # ===============================================================

    def __str__(self):

        return (
            f"StateManager("
            f"current_state="
            f"{self.current_state.value})"
        )


# ===================================================================
# STANDALONE VALIDATION
# ===================================================================

if __name__ == "__main__":

    manager = StateManager()

    print("\nInitial State:\n")

    print(manager.export_state())

    manager.transition(
        TrainingState.VALIDATING_ENVIRONMENT
    )

    manager.transition(
        TrainingState.LOADING_CONFIGURATION
    )

    manager.transition(
        TrainingState.LOADING_DATASETS
    )

    manager.transition(
        TrainingState.PREPROCESSING
    )

    manager.transition(
        TrainingState.BUILDING_MODEL
    )

    manager.transition(
        TrainingState.TRAINING
    )

    manager.transition(
        TrainingState.CHECKPOINTING
    )

    manager.transition(
        TrainingState.TRAINING
    )

    manager.transition(
        TrainingState.COMPLETED
    )

    print("\nFinal State:\n")

    print(manager.export_state())
