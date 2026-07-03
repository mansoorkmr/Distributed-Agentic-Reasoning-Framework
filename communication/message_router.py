"""
Distributed Agentic Reasoning Framework (DARF)

Message Router

Routes messages to registered agents.
"""

from __future__ import annotations

import json

from typing import Dict
from typing import Optional

from communication.message import Message
from communication.message_bus import MessageBus


class MessageRouter:

    def __init__(
        self,
        bus: Optional[MessageBus] = None,
    ):

        self.bus = bus or MessageBus()

        self.routes: Dict[str, object] = {}

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register(
        self,
        agent,
    ) -> None:

        self.routes[agent.agent_id] = agent

    def unregister(
        self,
        agent_id: str,
    ) -> None:

        self.routes.pop(agent_id, None)

    # ---------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------

    def contains(
        self,
        agent_id: str,
    ) -> bool:

        return agent_id in self.routes

    def get(
        self,
        agent_id: str,
    ):

        return self.routes.get(agent_id)

    # ---------------------------------------------------------
    # Routing
    # ---------------------------------------------------------

    def route(
        self,
        message: Message,
    ) -> bool:

        if message.is_broadcast():

            return self.bus.publish(message)

        if message.receiver not in self.routes:

            return False

        return self.bus.publish(message)

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def route_count(
        self,
    ) -> int:

        return len(self.routes)

    def is_empty(
        self,
    ) -> bool:

        return len(self.routes) == 0

    def clear(
        self,
    ) -> None:

        self.routes.clear()

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(
        self,
    ) -> Dict:

        return {

            "routes": list(self.routes.keys()),

            "route_count": self.route_count(),

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
    ) -> str:

        return f"MessageRouter({self.route_count()} routes)"

    def __repr__(
        self,
    ) -> str:

        return f"<MessageRouter routes={self.route_count()}>"