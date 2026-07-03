"""
Distributed Agentic Reasoning Framework (DARF)

Runtime Exceptions
"""

from __future__ import annotations


class RuntimeError(Exception):
    """
    Base runtime exception.
    """
    pass


class RuntimeInitializationError(RuntimeError):
    """
    Runtime failed during initialization.
    """
    pass


class RuntimeNotReadyError(RuntimeError):
    """
    Runtime is not ready.
    """
    pass


class RuntimeExecutionError(RuntimeError):
    """
    Runtime execution failed.
    """
    pass


class RuntimeShutdownError(RuntimeError):
    """
    Runtime shutdown failed.
    """
    pass


class RuntimeRegistryError(RuntimeError):
    """
    Runtime registry failure.
    """
    pass


class RuntimeConfigurationError(RuntimeError):
    """
    Invalid runtime configuration.
    """
    pass