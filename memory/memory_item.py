"""
Distributed Agentic Reasoning Framework (DARF)

Memory Item

Purpose
-------
Represents a single memory record shared across all memory
subsystems.

Responsibilities
----------------
- Store memory content
- Metadata
- Timestamps
- Serialization

Thread Safety
-------------
Thread-safe.
"""

from __future__ import annotations

import json
import uuid

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime
from datetime import timezone

from typing import Any
from typing import Dict

__all__ = [
    "MemoryItem",
]

def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
    )

@dataclass(slots=True)
class MemoryItem:
    """
    Canonical memory object.
    """

    memory_id: str = field(
        default_factory=lambda:
        f"MEM-{uuid.uuid4().hex.upper()}"
    )

    key: str = ""

    value: Any = None

    created_at: str = field(
        default_factory=_utc_now
    )

    updated_at: str = field(
        default_factory=_utc_now
    )

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
    
    # =======================================================
    # UPDATE
    # =======================================================

    def update(
        self,
        value: Any,
    ) -> None:

        self.value = value

        self.updated_at = _utc_now()
        
    # =======================================================
    # SERIALIZATION
    # =======================================================

    def to_dict(
        self,
    ) -> Dict[
        str,
        Any,
    ]:

        return {

            "memory_id": self.memory_id,

            "key": self.key,

            "value": self.value,

            "created_at": self.created_at,

            "updated_at": self.updated_at,

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

            default=str,

        )
        
    # =======================================================
    # REPRESENTATION
    # =======================================================

    def __str__(
        self,
    ) -> str:
        
        return f"{self.key}"

    def __repr__(
        self,
    ) -> str:

        return (

            f"<MemoryItem "

            f"key='{self.key}'>"

        )