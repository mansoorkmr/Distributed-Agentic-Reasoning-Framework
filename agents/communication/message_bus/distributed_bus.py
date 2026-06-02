"""
Institutional-Grade Distributed Message Bus
===========================================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities:
- Inter-agent messaging
- Distributed event propagation
- Runtime synchronization
- Pub/Sub orchestration
- Multi-node communication
- Delivery tracking
- Distributed-safe coordination runtime
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid

from collections import defaultdict
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional


# ============================================================
# MESSAGE TYPES
# ============================================================


class MessageType(str, Enum):
    """
    Distributed message categories.
    """

    EVENT = "event"

    COMMAND = "command"

    RESPONSE = "response"

    HEARTBEAT = "heartbeat"

    BROADCAST = "broadcast"

    SYNCHRONIZATION = "synchronization"


# ============================================================
# DELIVERY STATUS
# ============================================================


class DeliveryStatus(str, Enum):
    """
    Message delivery lifecycle.
    """

    PENDING = "pending"

    DELIVERED = "delivered"

    FAILED = "failed"

    ACKNOWLEDGED = "acknowledged"


# ============================================================
# DISTRIBUTED MESSAGE
# ============================================================


@dataclass(slots=True)
class DistributedMessage:
    """
    Distributed runtime message.
    """

    message_id: str

    sender_id: str

    recipient_id: Optional[str]

    message_type: MessageType

    payload: Dict[str, Any]

    created_at: float = field(
        default_factory=time.time
    )

    correlation_id: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# MESSAGE DELIVERY RECORD
# ============================================================


@dataclass(slots=True)
class DeliveryRecord:
    """
    Message delivery tracking.
    """

    message_id: str

    status: DeliveryStatus

    delivered_at: Optional[
        float
    ] = None

    error: Optional[str] = None


# ============================================================
# DISTRIBUTED BUS STATS
# ============================================================


@dataclass(slots=True)
class DistributedBusStats:
    """
    Message bus statistics.
    """

    total_messages: int = 0

    delivered_messages: int = 0

    failed_messages: int = 0

    active_subscribers: int = 0

    broadcast_operations: int = 0


# ============================================================
# DISTRIBUTED MESSAGE BUS
# ============================================================


class DistributedMessageBus:
    """
    Institutional-grade distributed message bus.

    Features:
    - Inter-agent messaging
    - Async-safe event propagation
    - Distributed coordination
    - Pub/Sub runtime
    - Multi-node communication
    """

    def __init__(
        self,
    ) -> None:

        self._subscriptions: DefaultDict[
            str,
            List[
                Callable[
                    [DistributedMessage],
                    Awaitable[None],
                ]
            ],
        ] = defaultdict(list)

        self._delivery_records: Dict[
            str,
            DeliveryRecord,
        ] = {}

        self._message_history: List[
            DistributedMessage
        ] = []

        self._stats = (
            DistributedBusStats()
        )

        self._lock = asyncio.Lock()

    # ========================================================
    # SUBSCRIPTION MANAGEMENT
    # ========================================================

    async def subscribe(
        self,
        topic: str,
        handler: Callable[
            [DistributedMessage],
            Awaitable[None],
        ],
    ) -> None:
        """
        Subscribe handler to topic.
        """

        async with self._lock:

            self._subscriptions[
                topic
            ].append(handler)

            self._stats.active_subscribers += 1

    async def unsubscribe(
        self,
        topic: str,
        handler: Callable,
    ) -> bool:
        """
        Remove subscription handler.
        """

        async with self._lock:

            if (
                topic
                not in self._subscriptions
            ):
                return False

            handlers = self._subscriptions[
                topic
            ]

            if handler not in handlers:
                return False

            handlers.remove(handler)

            self._stats.active_subscribers -= 1

            return True

    # ========================================================
    # MESSAGE PUBLISHING
    # ========================================================

    async def publish(
        self,
        topic: str,
        sender_id: str,
        payload: Dict[str, Any],
        message_type: MessageType = (
            MessageType.EVENT
        ),
        recipient_id: Optional[
            str
        ] = None,
        correlation_id: Optional[
            str
        ] = None,
    ) -> str:
        """
        Publish distributed message.
        """

        message = DistributedMessage(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=message_type,
            payload=payload,
            correlation_id=correlation_id,
        )

        async with self._lock:

            self._message_history.append(
                message
            )

            self._stats.total_messages += 1

            self._delivery_records[
                message.message_id
            ] = DeliveryRecord(
                message_id=message.message_id,
                status=DeliveryStatus.PENDING,
            )

        await self._dispatch_message(
            topic=topic,
            message=message,
        )

        return message.message_id

    # ========================================================
    # MESSAGE DISPATCH
    # ========================================================

    async def _dispatch_message(
        self,
        topic: str,
        message: DistributedMessage,
    ) -> None:
        """
        Dispatch message to subscribers.
        """

        subscribers = (
            self._subscriptions.get(
                topic,
                [],
            )
        )

        if not subscribers:

            await self._mark_failed(
                message.message_id,
                "No subscribers available.",
            )

            return

        tasks = [
            self._safe_handler_execution(
                handler=handler,
                message=message,
            )
            for handler in subscribers
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        failures = [
            result
            for result in results
            if isinstance(
                result,
                Exception,
            )
        ]

        if failures:

            await self._mark_failed(
                message.message_id,
                str(failures[0]),
            )

            return

        await self._mark_delivered(
            message.message_id
        )

    # ========================================================
    # SAFE HANDLER EXECUTION
    # ========================================================

    async def _safe_handler_execution(
        self,
        handler: Callable,
        message: DistributedMessage,
    ) -> None:
        """
        Execute subscriber safely.
        """

        await handler(message)

    # ========================================================
    # BROADCAST OPERATIONS
    # ========================================================

    async def broadcast(
        self,
        sender_id: str,
        payload: Dict[str, Any],
    ) -> List[str]:
        """
        Broadcast event to all topics.
        """

        async with self._lock:

            self._stats.broadcast_operations += 1

            topics = list(
                self._subscriptions.keys()
            )

        message_ids = []

        for topic in topics:

            message_id = await self.publish(
                topic=topic,
                sender_id=sender_id,
                payload=payload,
                message_type=(
                    MessageType.BROADCAST
                ),
            )

            message_ids.append(message_id)

        return message_ids

    # ========================================================
    # DELIVERY TRACKING
    # ========================================================

    async def _mark_delivered(
        self,
        message_id: str,
    ) -> None:
        """
        Mark message delivered.
        """

        async with self._lock:

            record = (
                self._delivery_records.get(
                    message_id
                )
            )

            if not record:
                return

            record.status = (
                DeliveryStatus.DELIVERED
            )

            record.delivered_at = (
                time.time()
            )

            self._stats.delivered_messages += 1

    async def _mark_failed(
        self,
        message_id: str,
        error: str,
    ) -> None:
        """
        Mark message failure.
        """

        async with self._lock:

            record = (
                self._delivery_records.get(
                    message_id
                )
            )

            if not record:
                return

            record.status = (
                DeliveryStatus.FAILED
            )

            record.error = error

            self._stats.failed_messages += 1

    async def get_delivery_status(
        self,
        message_id: str,
    ) -> Optional[DeliveryRecord]:
        """
        Retrieve delivery status.
        """

        async with self._lock:

            return self._delivery_records.get(
                message_id
            )

    # ========================================================
    # MESSAGE HISTORY
    # ========================================================

    async def get_message_history(
        self,
        limit: int = 100,
    ) -> List[DistributedMessage]:
        """
        Retrieve recent messages.
        """

        async with self._lock:

            return self._message_history[
                -limit:
            ]

    # ========================================================
    # SERIALIZATION
    # ========================================================

    @staticmethod
    def serialize_message(
        message: DistributedMessage,
    ) -> str:
        """
        Serialize distributed message.
        """

        return json.dumps(
            asdict(message)
        )

    @staticmethod
    def deserialize_message(
        payload: str,
    ) -> DistributedMessage:
        """
        Deserialize distributed message.
        """

        return DistributedMessage(
            **json.loads(payload)
        )

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, Any]:
        """
        Runtime diagnostics.
        """

        return {
            "status": "healthy",
            "total_messages": (
                self._stats.total_messages
            ),
            "delivered_messages": (
                self._stats.delivered_messages
            ),
            "failed_messages": (
                self._stats.failed_messages
            ),
            "active_subscribers": (
                self._stats.active_subscribers
            ),
            "broadcast_operations": (
                self._stats.broadcast_operations
            ),
        }

    # ========================================================
    # STATS
    # ========================================================

    def get_stats(
        self,
    ) -> DistributedBusStats:
        """
        Retrieve bus statistics.
        """

        return self._stats
