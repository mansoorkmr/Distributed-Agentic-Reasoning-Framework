"""
Institutional-Grade Semantic Memory System
==========================================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities:
- Persistent semantic knowledge memory
- Embedding-based retrieval
- Concept storage/indexing
- Semantic similarity search
- Long-term cognition persistence
- Knowledge retrieval orchestration
- Distributed-safe vector memory
"""

from __future__ import annotations

import asyncio
import json
import math
import time
import uuid

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple


# ============================================================
# SEMANTIC MEMORY ENTRY
# ============================================================


@dataclass(slots=True)
class SemanticMemoryEntry:
    """
    Represents semantic knowledge memory.
    """

    memory_id: str

    concept: str

    content: Dict[str, Any]

    embedding: List[float]

    created_at: float = field(
        default_factory=time.time
    )

    access_count: int = 0

    importance_score: float = 1.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def touch(self) -> None:
        """
        Update access statistics.
        """

        self.access_count += 1


# ============================================================
# SEMANTIC SEARCH RESULT
# ============================================================


@dataclass(slots=True)
class SemanticSearchResult:
    """
    Semantic retrieval result.
    """

    memory_id: str

    concept: str

    similarity_score: float

    content: Dict[str, Any]


# ============================================================
# SEMANTIC MEMORY STATS
# ============================================================


@dataclass(slots=True)
class SemanticMemoryStats:
    """
    Semantic memory statistics.
    """

    total_memories: int = 0

    retrieval_operations: int = 0

    insertions: int = 0

    persisted_entries: int = 0


# ============================================================
# SEMANTIC MEMORY ENGINE
# ============================================================


class SemanticMemory:
    """
    Institutional-grade semantic memory runtime.

    Features:
    - Semantic vector memory
    - Embedding similarity retrieval
    - Persistent knowledge storage
    - Concept indexing
    - Distributed-safe cognition
    """

    def __init__(
        self,
        storage_path: str = "memory/semantic",
    ) -> None:

        self.storage_path = Path(storage_path)

        self.storage_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._memories: Dict[
            str,
            SemanticMemoryEntry,
        ] = {}

        self._stats = SemanticMemoryStats()

        self._lock = asyncio.Lock()

    # ========================================================
    # MEMORY INSERTION
    # ========================================================

    async def add_memory(
        self,
        concept: str,
        content: Dict[str, Any],
        embedding: List[float],
        importance_score: float = 1.0,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> str:
        """
        Store semantic knowledge.
        """

        async with self._lock:

            memory = SemanticMemoryEntry(
                memory_id=str(uuid.uuid4()),
                concept=concept,
                content=content,
                embedding=embedding,
                importance_score=importance_score,
                metadata=metadata or {},
            )

            self._memories[
                memory.memory_id
            ] = memory

            self._stats.insertions += 1

            self._stats.total_memories = len(
                self._memories
            )

            await self._persist_memory(
                memory
            )

            return memory.memory_id

    # ========================================================
    # SEMANTIC RETRIEVAL
    # ========================================================

    async def semantic_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[SemanticSearchResult]:
        """
        Perform semantic similarity search.
        """

        async with self._lock:

            self._stats.retrieval_operations += 1

            scored_results: List[
                Tuple[
                    float,
                    SemanticMemoryEntry,
                ]
            ] = []

            for memory in self._memories.values():

                similarity = (
                    self._cosine_similarity(
                        query_embedding,
                        memory.embedding,
                    )
                )

                scored_results.append(
                    (
                        similarity,
                        memory,
                    )
                )

            scored_results.sort(
                key=lambda item: item[0],
                reverse=True,
            )

            results = []

            for (
                similarity,
                memory,
            ) in scored_results[:top_k]:

                memory.touch()

                results.append(
                    SemanticSearchResult(
                        memory_id=memory.memory_id,
                        concept=memory.concept,
                        similarity_score=similarity,
                        content=memory.content,
                    )
                )

            return results

    # ========================================================
    # CONCEPT RETRIEVAL
    # ========================================================

    async def get_memory(
        self,
        memory_id: str,
    ) -> Optional[
        SemanticMemoryEntry
    ]:
        """
        Retrieve semantic memory by ID.
        """

        async with self._lock:

            memory = self._memories.get(
                memory_id
            )

            if memory:
                memory.touch()

            return memory

    async def search_by_concept(
        self,
        concept: str,
    ) -> List[
        SemanticMemoryEntry
    ]:
        """
        Search memories by concept.
        """

        async with self._lock:

            query = concept.lower()

            return [
                memory
                for memory in self._memories.values()
                if query
                in memory.concept.lower()
            ]

    # ========================================================
    # KNOWLEDGE PERSISTENCE
    # ========================================================

    async def _persist_memory(
        self,
        memory: SemanticMemoryEntry,
    ) -> None:
        """
        Persist semantic memory to disk.
        """

        memory_path = (
            self.storage_path
            / f"{memory.memory_id}.json"
        )

        with open(
            memory_path,
            "w",
            encoding="utf-8",
        ) as memory_file:

            json.dump(
                asdict(memory),
                memory_file,
                indent=2,
            )

        self._stats.persisted_entries += 1

    async def load_persisted_memories(
        self,
    ) -> None:
        """
        Restore persisted memories.
        """

        async with self._lock:

            for path in self.storage_path.glob(
                "*.json"
            ):

                with open(
                    path,
                    "r",
                    encoding="utf-8",
                ) as memory_file:

                    payload = json.load(
                        memory_file
                    )

                memory = (
                    SemanticMemoryEntry(
                        **payload
                    )
                )

                self._memories[
                    memory.memory_id
                ] = memory

            self._stats.total_memories = len(
                self._memories
            )

    # ========================================================
    # VECTOR OPERATIONS
    # ========================================================

    @staticmethod
    def _cosine_similarity(
        vector_a: List[float],
        vector_b: List[float],
    ) -> float:
        """
        Compute cosine similarity.
        """

        if (
            not vector_a
            or not vector_b
        ):
            return 0.0

        dot_product = sum(
            a * b
            for a, b in zip(
                vector_a,
                vector_b,
            )
        )

        magnitude_a = math.sqrt(
            sum(
                value * value
                for value in vector_a
            )
        )

        magnitude_b = math.sqrt(
            sum(
                value * value
                for value in vector_b
            )
        )

        if (
            magnitude_a == 0
            or magnitude_b == 0
        ):
            return 0.0

        return (
            dot_product
            / (
                magnitude_a
                * magnitude_b
            )
        )

    # ========================================================
    # KNOWLEDGE RANKING
    # ========================================================

    async def get_high_value_memories(
        self,
        threshold: float = 0.8,
    ) -> List[
        SemanticMemoryEntry
    ]:
        """
        Retrieve important knowledge.
        """

        async with self._lock:

            return sorted(
                [
                    memory
                    for memory
                    in self._memories.values()
                    if (
                        memory.importance_score
                        >= threshold
                    )
                ],
                key=lambda memory: (
                    memory.importance_score
                ),
                reverse=True,
            )

    # ========================================================
    # STATISTICS
    # ========================================================

    def get_stats(
        self,
    ) -> SemanticMemoryStats:
        """
        Retrieve runtime statistics.
        """

        return self._stats

    # ========================================================
    # DEBUGGING
    # ========================================================

    async def dump_memories(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Export semantic memories.
        """

        async with self._lock:

            return [
                asdict(memory)
                for memory
                in self._memories.values()
            ]
