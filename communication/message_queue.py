"""
Distributed Agentic Reasoning Framework (DARF)

Message Queue
"""

from __future__ import annotations

import json
from collections import deque

from typing import Deque
from typing import Dict
from typing import List

from communication.message import Message
from communication.communication_policy import CommunicationPolicy

class MessageQueue:

    def __init__(
        self,
        policy: CommunicationPolicy | None = None,
    ):

        self.policy = policy or CommunicationPolicy()

        self._queue: Deque[Message] = deque()
        
    def enqueue(
        self,
        message: Message,
    ) -> bool:

        if not self.policy.has_queue_capacity(
            len(self._queue)
        ):
            return False

        self._queue.append(message)

        return True

    def dequeue(
        self,
    ) -> Message | None:

        if not self._queue:
            return None

        return self._queue.popleft()

    def peek(
        self,
    ) -> Message | None:

        if not self._queue:
            return None

        return self._queue[0]
        
    def clear(
        self,
    ):

        self._queue.clear()

    def is_empty(
        self,
    ) -> bool:

        return len(self._queue) == 0

    def size(
        self,
    ) -> int:

        return len(self._queue)

    def messages(
        self,
    ) -> List[Message]:

        return list(self._queue)
        
    def to_dict(
        self,
    ) -> Dict:

        return {

            "size": self.size(),

            "messages": [

                message.to_dict()

                for message in self._queue

            ],

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
        
    def __str__(
        self,
    ) -> str:

        return (

            f"MessageQueue("

            f"{self.size()} messages)"

        )

    def __repr__(
        self,
    ) -> str:

        return (

            f"<MessageQueue "

            f"size={self.size()}>"

        )