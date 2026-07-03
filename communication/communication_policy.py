"""
Distributed Agentic Reasoning Framework (DARF)

Communication Policy

Defines communication behavior between agents.

Responsibilities
----------------
- Queue limits
- Broadcast policy
- Delivery timeout
- Retry policy
- Message TTL
"""
from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict

@dataclass(slots=True)
class CommunicationPolicy:

    max_queue_size: int = 1000

    allow_broadcast: bool = True

    delivery_timeout: float = 30.0

    max_retries: int = 3

    message_ttl: float = 300.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"
    
    def broadcast_enabled(
        self,
    ) -> bool:

        return self.allow_broadcast

    def has_queue_capacity(
        self,
        current_size: int,
    ) -> bool:

        return current_size < self.max_queue_size

    def retries_allowed(
        self,
    ) -> bool:

        return self.max_retries > 0

    def ttl_enabled(
        self,
    ) -> bool:

        return self.message_ttl > 0
        
    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return {

            "max_queue_size": self.max_queue_size,

            "allow_broadcast": self.allow_broadcast,

            "delivery_timeout": self.delivery_timeout,

            "max_retries": self.max_retries,

            "message_ttl": self.message_ttl,

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(
        self,
    ) -> str:

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )
        
    def __str__(
        self,
    ) -> str:

        return (

            f"CommunicationPolicy("

            f"queue={self.max_queue_size})"

        )

    def __repr__(
        self,
    ) -> str:

        return (

            "<CommunicationPolicy "

            f"queue={self.max_queue_size} "

            f"retries={self.max_retries}>"

        )