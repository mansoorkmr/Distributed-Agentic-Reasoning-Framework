"""
Distributed Agentic Reasoning Framework (DARF)

Communication Exceptions

Defines all communication-related exceptions.
"""

from __future__ import annotations


class CommunicationError(Exception):
    """
    Base class for all communication exceptions.
    """

    pass


class MessageQueueFullError(CommunicationError):
    """
    Raised when the message queue is full.
    """

    pass


class RouteNotFoundError(CommunicationError):
    """
    Raised when a destination agent is not registered.
    """

    pass


class MessageDeliveryError(CommunicationError):
    """
    Raised when a message cannot be delivered.
    """

    pass


class BroadcastDisabledError(CommunicationError):
    """
    Raised when broadcast is disabled by policy.
    """

    pass


class InvalidMessageError(CommunicationError):
    """
    Raised when a message object is invalid.
    """

    pass


class SerializationError(CommunicationError):
    """
    Raised when serialization/deserialization fails.
    """

    pass