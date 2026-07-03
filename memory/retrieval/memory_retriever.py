"""
Distributed Agentic Reasoning Framework (DARF)

Memory Retriever

Purpose
-------
Provides retrieval operations over semantic memory.

Responsibilities
----------------
- Exact lookup
- Prefix lookup
- Keyword search
- List stored knowledge

This class is intentionally backend-agnostic. Later versions
will integrate FAISS and embedding-based semantic search.
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict
from typing import List

from memory.semantic_memory import SemanticMemory

__all__ = [
    "MemoryRetriever",
]
# ============================================================
# MEMORY RETRIEVER
# ============================================================

@dataclass(slots=True)
class MemoryRetriever:

    memory: SemanticMemory = field(
        default_factory=SemanticMemory
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"
        # ========================================================
    # EXACT RETRIEVAL
    # ========================================================

    def retrieve(
        self,
        key: str,
    ) -> Any:

        return self.memory.recall(
            key,
        )
        # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query: str,
    ) -> Dict[str, Any]:

        results = {}

        query = query.lower()

        for key in self.memory.store.keys():

            if query in key.lower():

                results[key] = self.memory.recall(
                    key,
                )

        return results
        # ========================================================
    # KEYS
    # ========================================================

    def keys(
        self,
    ) -> List[str]:

        return self.memory.store.keys()
        # ========================================================
    # STATISTICS
    # ========================================================

    def count(
        self,
    ) -> int:

        return self.memory.count()

    def is_empty(
        self,
    ) -> bool:

        return self.memory.is_empty()
        # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:

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
            f"MemoryRetriever("
            f"{self.count()} memories)"
        )

    def __repr__(
        self,
    ) -> str:

        return (
            f"<MemoryRetriever "
            f"count={self.count()}>"
        )
    