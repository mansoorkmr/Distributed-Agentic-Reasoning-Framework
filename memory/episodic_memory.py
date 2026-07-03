"""
Distributed Agentic Reasoning Framework (DARF)

Episodic Memory

Purpose
-------
Stores chronological experiences, interactions, and execution history.

Responsibilities
----------------
- Append episodes
- Retrieve episodes
- Maintain chronological order

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
    "EpisodicMemory",
]
# ============================================================
# EPISODIC MEMORY
# ============================================================

@dataclass(slots=True)
class EpisodicMemory:
    """
    Chronological memory.
    """

    episodes: List[
        MemoryItem
    ] = field(
        default_factory=list
    )

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )

    version: str = "1.0"
        # ========================================================
    # API
    # ========================================================

    def add(
        self,
        item: MemoryItem,
    ) -> None:

        self.episodes.append(
            item,
        )

    def latest(
        self,
    ) -> MemoryItem | None:

        if not self.episodes:

            return None

        return self.episodes[-1]

    def get(
        self,
        index: int,
    ) -> MemoryItem:

        return self.episodes[index]

    def clear(
        self,
    ) -> None:

        self.episodes.clear()
            # ========================================================
    # QUERIES
    # ========================================================

    def count(
        self,
    ) -> int:

        return len(
            self.episodes
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

            "episodes": [

                item.key

                for item

                in self.episodes

            ],

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
            f"EpisodicMemory("
            f"{self.count()} episodes)"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<EpisodicMemory "
            f"count={self.count()}>"
        )