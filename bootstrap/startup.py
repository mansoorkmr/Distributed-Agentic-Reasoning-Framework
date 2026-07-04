"""
Application bootstrap.
"""

from __future__ import annotations

from app_core import DARFApplication

_application: DARFApplication | None = None


def initialize() -> DARFApplication:
    """
    Initialize the DARF application once.
    """
    global _application

    if _application is None:
        _application = DARFApplication()

    return _application


def get_application() -> DARFApplication:
    """
    Return the initialized application.
    """
    if _application is None:
        return initialize()

    return _application


def reset() -> None:
    """
    Reset bootstrap (mainly for tests).
    """
    global _application
    _application = None