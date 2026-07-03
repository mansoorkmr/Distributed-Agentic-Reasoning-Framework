"""
Distributed Agentic Reasoning Framework (DARF)

Message Bus

Provides communication between agents through a shared queue.
"""

from __future__ import annotations

import json

from typing import Dict
from typing import List

from communication.message import Message
from communication.message_queue import MessageQueue
from communication.communication_policy import CommunicationPolicy


class MessageBus:

    def __init__(
        self,
        policy: CommunicationPolicy | None = None,
    ):

        self.policy = policy or CommunicationPolicy()

        self.queue = MessageQueue(self.policy)

    # ---------------------------------------------------------
    # Publish
    # ---------------------------------------------------------

    def publish(
        self,
        message: Message,
    ) -> bool:

        return self.queue.enqueue(message)

    # ---------------------------------------------------------
    # Receive
    # ---------------------------------------------------------

    def receive(
        self,
    ) -> Message | None:

        return self.queue.dequeue()

    # ---------------------------------------------------------
    # Broadcast
    # ---------------------------------------------------------

    def broadcast(
        self,
        sender: str,
        payload,
        message_type: str = "broadcast",
    ) -> bool:

        if not self.policy.broadcast_enabled():

            return False

        message = Message(

            sender=sender,

            receiver=None,

            message_type=message_type,

            payload=payload,

        )

        return self.publish(message)

    # ---------------------------------------------------------
    # Queue Utilities
    # ---------------------------------------------------------

    def pending_messages(
        self,
    ) -> int:

        return self.queue.size()

    def is_empty(
        self,
    ) -> bool:

        return self.queue.is_empty()

    def clear(
        self,
    ):

        self.queue.clear()

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(
        self,
    ) -> Dict:

        return {

            "queue": self.queue.to_dict(),

            "policy": self.policy.to_dict(),

            "version": "1.0",

        }

    def to_json(
        self,
    ) -> str:

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(
        self,
    ):

        return (

            f"MessageBus("

            f"{self.pending_messages()} pending)"

        )

    def __repr__(
        self,
    ):

        return (

            "<MessageBus "

            f"pending={self.pending_messages()}>"

        )