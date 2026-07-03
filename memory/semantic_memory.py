"""
Distributed Agentic Reasoning Framework (DARF)

Semantic Memory

Purpose
-------
Stores persistent facts and knowledge that can be retrieved
by key.

Responsibilities
----------------
- Store facts
- Update knowledge
- Retrieve knowledge
- Remove knowledge

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

from memory.memory_store import MemoryStore
from memory.memory_item import MemoryItem

__all__ = [
    "SemanticMemory",
]
# ============================================================
# SEMANTIC MEMORY
# ============================================================


@dataclass(slots=True)
class SemanticMemory:
    """
    Long-term knowledge memory.
    """

    store: MemoryStore = field(
        default_factory=MemoryStore
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

    def remember(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.store.add(

            MemoryItem(

                key=key,

                value=value,

            )

        )

    def recall(
        self,
        key: str,
    ) -> Any:

        item = self.store.get(
            key,
        )

        if item is None:

            return None

        return item.value

    def forget(
        self,
        key: str,
    ) -> None:

        self.store.remove(
            key,
        )

    def clear(
        self,
    ) -> None:

        self.store.clear()
            # ========================================================
    # QUERIES
    # ========================================================

    def contains(
        self,
        key: str,
    ) -> bool:

        return self.store.contains(
            key,
        )

    def count(
        self,
    ) -> int:

        return self.store.count()

    def is_empty(
        self,
    ) -> bool:

        return self.store.is_empty()
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

            "keys": self.store.keys(),

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
            f"SemanticMemory("
            f"{self.count()} facts)"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<SemanticMemory "
            f"count={self.count()}>"
        )