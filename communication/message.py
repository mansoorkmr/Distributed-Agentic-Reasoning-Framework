"""
Distributed Agentic Reasoning Framework (DARF)

Communication Message
"""

from __future__ import annotations

import json
import uuid

from datetime import datetime

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import Optional


@dataclass(slots=True)
class Message:

    message_id: str = field(
        default_factory=lambda:
        f"MSG-{uuid.uuid4().hex.upper()}"
    )

    sender: Optional[str] = None

    receiver: Optional[str] = None

    message_type: str = "generic"

    payload: Any = None

    created_at: str = field(
        default_factory=lambda:
        datetime.utcnow().isoformat()
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"

    def is_direct(self) -> bool:

        return self.receiver is not None

    def is_broadcast(self) -> bool:

        return self.receiver is None

    def payload_type(self) -> str:

        if self.payload is None:
            return "None"

        return type(self.payload).__name__

    def to_dict(self):

        return {

            "message_id": self.message_id,

            "sender": self.sender,

            "receiver": self.receiver,

            "message_type": self.message_type,

            "payload": self.payload,

            "created_at": self.created_at,

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(self):

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

            default=str,

        )

    def __str__(self):

        return f"Message({self.message_type})"

    def __repr__(self):

        return f"<Message id='{self.message_id}'>"
    