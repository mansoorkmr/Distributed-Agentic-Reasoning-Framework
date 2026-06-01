from __future__ import annotations

"""
Global Configuration System
===========================

This module provides a **strongly-typed, immutable, and validated configuration layer**
for the entire system.

It eliminates:
    ✔ Environment inconsistency
    ✔ Path errors (HF cache, checkpoints)
    ✔ Silent misconfiguration
    ✔ Runtime drift across HPC jobs

Design Patterns:
    - Singleton Pattern (module-level instance)
    - Factory Pattern (environment loading)
    - Guard Clauses (fail-fast validation)
    - Immutable Object Pattern (dataclass frozen=True)

Complexity:
    - Initialization: O(n) for environment variables
    - Access: O(1)
"""

import os
from dataclasses import dataclass, field
from typing import Final


# =========================================================
# EXCEPTION HIERARCHY
# =========================================================

class ConfigError(Exception):
    """Base configuration error."""
    pass


class ConfigValidationError(ConfigError):
    """Raised when configuration is invalid."""
    pass


# =========================================================
# VALIDATION UTILITIES
# =========================================================

def _validate_path(path: str, must_exist: bool = False) -> str:
    """
    Validate filesystem path.

    Complexity: O(1)
    """
    if not isinstance(path, str) or not path.strip():
        raise ConfigValidationError(f"Invalid path: {path}")

    if must_exist and not os.path.exists(path):
        raise ConfigValidationError(f"Path does not exist: {path}")

    return path


def _validate_positive_int(value: int, name: str) -> int:
    """
    Validate positive integer.

    Complexity: O(1)
    """
    if not isinstance(value, int) or value <= 0:
        raise ConfigValidationError(f"{name} must be positive integer")
    return value


def _validate_float(value: float, name: str) -> float:
    """
    Validate float range.

    Complexity: O(1)
    """
    if not isinstance(value, float) or value <= 0:
        raise ConfigValidationError(f"{name} must be positive float")
    return value


# =========================================================
# SETTINGS DATA MODEL
# =========================================================

@dataclass(frozen=True)
class Settings:
    """
    Immutable configuration object.

    Guarantees:
        ✔ No runtime mutation
        ✔ Strong typing
        ✔ Validated at creation

    Complexity:
        O(n) initialization, O(1) access
    """

    # Core Paths
    PROJECT_ROOT: str
    HF_HOME: str
    CHECKPOINT_DIR: str

    # Training Parameters
    MAX_SEQ_LENGTH: int
    BATCH_SIZE: int
    LEARNING_RATE: float

    # System Flags
    OFFLINE_MODE: bool
    NUM_WORKERS: int

    # Internal validation executed automatically
    def __post_init__(self):
        object.__setattr__(self, "PROJECT_ROOT", _validate_path(self.PROJECT_ROOT))
        object.__setattr__(self, "HF_HOME", _validate_path(self.HF_HOME))
        object.__setattr__(self, "CHECKPOINT_DIR", _validate_path(self.CHECKPOINT_DIR))

        object.__setattr__(self, "MAX_SEQ_LENGTH", _validate_positive_int(self.MAX_SEQ_LENGTH, "MAX_SEQ_LENGTH"))
        object.__setattr__(self, "BATCH_SIZE", _validate_positive_int(self.BATCH_SIZE, "BATCH_SIZE"))
        object.__setattr__(self, "NUM_WORKERS", _validate_positive_int(self.NUM_WORKERS, "NUM_WORKERS"))

        object.__setattr__(self, "LEARNING_RATE", _validate_float(self.LEARNING_RATE, "LEARNING_RATE"))


# =========================================================
# FACTORY FUNCTION (ENV LOADER)
# =========================================================

def _load_settings() -> Settings:
    """
    Load configuration from environment variables.

    Design:
        Factory Pattern

    Complexity:
        O(n)
    """

    project_root = os.getenv(
        "PROJECT_ROOT",
        "/home/mansoor.wani/Distributed_Multi_Agent_AI_System"
    )

    hf_home = os.getenv(
        "HF_HOME",
        "/lustre/mansoor.wani/hf_cache"
    )

    checkpoint_dir = os.getenv(
        "CHECKPOINT_DIR",
        f"{project_root}/checkpoints/llm"
    )

    try:
        settings = Settings(
            PROJECT_ROOT=project_root,
            HF_HOME=hf_home,
            CHECKPOINT_DIR=checkpoint_dir,
            MAX_SEQ_LENGTH=int(os.getenv("MAX_SEQ_LENGTH", "512")),
            BATCH_SIZE=int(os.getenv("BATCH_SIZE", "4")),
            LEARNING_RATE=float(os.getenv("LEARNING_RATE", "5e-5")),
            OFFLINE_MODE=os.getenv("TRANSFORMERS_OFFLINE", "1") == "1",
            NUM_WORKERS=int(os.getenv("NUM_WORKERS", "2")),
        )
    except Exception as e:
        raise ConfigValidationError(f"Failed to load settings: {e}") from e

    return settings


# =========================================================
# SINGLETON INSTANCE
# =========================================================

settings: Final[Settings] = _load_settings()


# =========================================================
# RUNTIME SAFETY CHECKS
# =========================================================

def validate_runtime_environment() -> None:
    """
    Validate runtime environment.

    Ensures:
        ✔ HF cache accessible
        ✔ checkpoint directory safe
        ✔ environment consistency

    Complexity: O(1)
    """

    if settings.OFFLINE_MODE:
        if not os.path.exists(settings.HF_HOME):
            raise ConfigValidationError(
                f"HF cache not found in offline mode: {settings.HF_HOME}"
            )

    if not os.path.exists(settings.CHECKPOINT_DIR):
        os.makedirs(settings.CHECKPOINT_DIR, exist_ok=True)


# Execute validation at import time
validate_runtime_environment()
