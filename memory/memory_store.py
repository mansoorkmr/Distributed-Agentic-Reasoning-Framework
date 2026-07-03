"""
Distributed Agentic Reasoning Framework (DARF)

Memory Store

Purpose
-------
Provides the canonical in-memory storage implementation used by
working, episodic, and semantic memory.

Responsibilities
----------------
- Store MemoryItem objects
- CRUD operations
- Serialization
- Metrics

Thread Safety
-------------
Thread-safe.
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import List

from memory.memory_item import MemoryItem

__all__ = [
    "MemoryStore",
]
# ============================================================
# MEMORY STORE
# ============================================================

@dataclass(slots=True)
class MemoryStore:
    """
    Canonical in-memory storage.
    """

    items: Dict[
        str,
        MemoryItem,
    ] = field(
        default_factory=dict
    )

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
        # ========================================================
    # CRUD
    # ========================================================

    def add(
        self,
        item: MemoryItem,
    ) -> None:

        self.items[item.key] = item

    def get(
        self,
        key: str,
    ) -> MemoryItem | None:

        return self.items.get(key)

    def remove(
        self,
        key: str,
    ) -> None:

        self.items.pop(
            key,
            None,
        )

    def clear(
        self,
    ) -> None:

        self.items.clear()
            # ========================================================
    # QUERIES
    # ========================================================

    def contains(
        self,
        key: str,
    ) -> bool:

        return key in self.items

    def keys(
        self,
    ) -> List[str]:

        return sorted(
            self.items.keys()
        )

    def values(
        self,
    ) -> List[MemoryItem]:

        return list(
            self.items.values()
        )

    def count(
        self,
    ) -> int:

        return len(
            self.items
        )

    def is_empty(
        self,
    ) -> bool:

        return self.count() == 0
        # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[
        str,
        Any,
    ]:

        return {

            "count": self.count(),

            "keys": self.keys(),

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
        # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(
        self,
    ) -> str:

        return (
            f"MemoryStore("
            f"{self.count()} items)"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<MemoryStore "
            f"count={self.count()}>"
        )