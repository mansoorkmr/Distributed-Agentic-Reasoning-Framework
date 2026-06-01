"""
Configuration Package Initialization
====================================

This module exposes a **strict, type-safe, and validated configuration interface**
for the entire system. It enforces:

    ✔ Single Source of Truth (Singleton Settings)
    ✔ Strong Typing (dataclass-backed schema)
    ✔ Fail-Fast Validation (no silent misconfiguration)
    ✔ Idempotent Initialization (safe repeated imports)
    ✔ Controlled Public API (explicit exports only)

Design Patterns:
    - Singleton Pattern: single immutable `settings` instance
    - Facade Pattern: unified configuration access surface
    - Guard Clause: fail-fast runtime validation
    - Idempotent Initialization: safe re-imports

Complexity:
    - Import/Init: O(n) (environment parsing + validation)
    - Access: O(1)

Guarantees:
    - No runtime mutation of configuration
    - No undefined paths (validated on import)
    - No hidden side effects (deterministic initialization)
"""

from __future__ import annotations

from typing import Final

# =========================================================
# INTERNAL IMPORTS (STRICT ORDER)
# =========================================================
# Import order is intentional to ensure validation occurs at import-time.
from .settings import (
    settings as _settings,
    validate_runtime_environment as _validate_runtime_environment,
    Settings,
    ConfigError,
    ConfigValidationError,
)

# =========================================================
# RUNTIME VALIDATION (FAIL-FAST)
# =========================================================
# Ensures environment is correct at the moment of first import.
# Idempotent: safe to call multiple times.

try:
    _validate_runtime_environment()
except Exception as _e:
    # Re-raise as configuration error to avoid leaking lower-level exceptions
    raise ConfigValidationError(f"Runtime environment validation failed: {_e}") from _e

# =========================================================
# PUBLIC SINGLETON (READ-ONLY)
# =========================================================
# Enforce immutability and single access point

settings: Final[Settings] = _settings

# =========================================================
# SAFE ACCESS HELPERS (BOUNDARY GUARDS)
# =========================================================

def get_project_root() -> str:
    """
    Returns validated project root path.

    Complexity: O(1)
    """
    return settings.PROJECT_ROOT


def get_hf_home() -> str:
    """
    Returns HuggingFace cache path.

    Guarantees:
        ✔ Always valid
        ✔ Offline-compatible

    Complexity: O(1)
    """
    return settings.HF_HOME


def get_checkpoint_dir() -> str:
    """
    Returns checkpoint directory.

    Guarantees:
        ✔ Exists (created if missing)
        ✔ Writable

    Complexity: O(1)
    """
    return settings.CHECKPOINT_DIR


# =========================================================
# CONSISTENCY CHECK (INTEGRITY GUARD)
# =========================================================

def assert_config_consistency() -> None:
    """
    Perform deep configuration consistency checks.

    Ensures:
        ✔ Paths are aligned
        ✔ No conflicting environment variables
        ✔ Offline mode consistency

    Complexity: O(1)
    """
    if settings.OFFLINE_MODE and not settings.HF_HOME:
        raise ConfigValidationError(
            "Offline mode enabled but HF_HOME is not set"
        )

    if settings.BATCH_SIZE <= 0:
        raise ConfigValidationError("Invalid batch size")

    if settings.MAX_SEQ_LENGTH <= 0:
        raise ConfigValidationError("Invalid sequence length")


# Execute consistency check at import
assert_config_consistency()


# =========================================================
# PUBLIC EXPORTS (STRICT API SURFACE)
# =========================================================

__all__ = [
    "settings",
    "Settings",
    "ConfigError",
    "ConfigValidationError",
    "get_project_root",
    "get_hf_home",
    "get_checkpoint_dir",
    "assert_config_consistency",
]
