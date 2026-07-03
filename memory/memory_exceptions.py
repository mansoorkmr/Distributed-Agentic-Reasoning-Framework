"""
Distributed Agentic Reasoning Framework (DARF)

Memory Exceptions

Purpose
-------
Defines all exceptions raised by the memory subsystem.
"""

from __future__ import annotations

__all__ = [
    "MemoryError",
    "MemoryNotFoundError",
    "MemoryCapacityError",
    "MemoryPersistenceError",
    "MemoryRetrievalError",
]
# ============================================================
# BASE
# ============================================================

class MemoryError(Exception):
    """
    Base memory exception.
    """

    pass
# ============================================================
# NOT FOUND
# ============================================================

class MemoryNotFoundError(
    MemoryError,
):
    """
    Memory item not found.
    """

    pass
# ============================================================
# CAPACITY
# ============================================================

class MemoryCapacityError(
    MemoryError,
):
    """
    Memory capacity exceeded.
    """

    pass
# ============================================================
# PERSISTENCE
# ============================================================

class MemoryPersistenceError(
    MemoryError,
):
    """
    Persistence backend failure.
    """

    pass
# ============================================================
# RETRIEVAL
# ============================================================

class MemoryRetrievalError(
    MemoryError,
):
    """
    Retrieval failure.
    """

    pass
