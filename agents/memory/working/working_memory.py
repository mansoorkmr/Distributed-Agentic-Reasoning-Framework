"""
Institutional-Grade Working Memory System
=========================================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities:
- Short-term cognitive memory
- Active execution context
- Token-aware context management
- Runtime execution tracking
- Session-isolated memory
- Async-safe memory orchestration
- Snapshot/restore support
- Memory prioritization
- Context truncation
- Distributed runtime compatibility
"""

from __future__ import annotations

import asyncio
import time
import uuid

from collections import deque
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Deque
from typing import Dict
from typing import List
from typing import Optional


# ============================================================
# MEMORY ENTRY
# ============================================================


@dataclass(slots=True)
class MemoryEntry:
    """
    Represents a single working memory unit.
    """

    memory_id: str
    content: Any
    role: str
    token_count: int

    created_at: float = field(default_factory=time.time)

    priority_score: float = 1.0
    access_count: int = 0
    relevance_score: float = 1.0

    metadata: Dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        """
        Update memory access statistics.
        """

        self.access_count += 1


# ============================================================
# EXECUTION SNAPSHOT
# ============================================================


@dataclass(slots=True)
class ExecutionSnapshot:
    """
    Serializable execution snapshot.
    """

    snapshot_id: str

    session_id: str

    created_at: float

    memory_entries: List[Dict[str, Any]]

    execution_state: Dict[str, Any]


# ============================================================
# WORKING MEMORY STATS
# ============================================================


@dataclass(slots=True)
class WorkingMemoryStats:
    """
    Working memory runtime statistics.
    """

    total_memories: int = 0

    active_tokens: int = 0

    total_insertions: int = 0

    total_evictions: int = 0

    snapshot_count: int = 0


# ============================================================
# WORKING MEMORY ENGINE
# ============================================================


class WorkingMemory:
    """
    Institutional-grade working memory runtime.

    Features:
    - Token-aware context management
    - Session isolation
    - Async-safe execution
    - Context prioritization
    - Runtime snapshotting
    - Memory eviction
    - Cognitive execution support
    """

    def __init__(
        self,
        session_id: str,
        max_tokens: int = 8192,
        max_entries: int = 256,
    ) -> None:

        self.session_id = session_id

        self.max_tokens = max_tokens

        self.max_entries = max_entries

        self._memory: Deque[MemoryEntry] = deque()

        self._stats = WorkingMemoryStats()

        self._execution_state: Dict[str, Any] = {}

        self._lock = asyncio.Lock()

    # ========================================================
    # MEMORY INSERTION
    # ========================================================

    async def add_memory(
        self,
        content: Any,
        role: str,
        token_count: int,
        priority_score: float = 1.0,
        relevance_score: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Insert memory into working memory.
        """

        async with self._lock:

            memory = MemoryEntry(
                memory_id=str(uuid.uuid4()),
                content=content,
                role=role,
                token_count=token_count,
                priority_score=priority_score,
                relevance_score=relevance_score,
                metadata=metadata or {},
            )

            self._memory.append(memory)

            self._stats.total_insertions += 1

            self._stats.total_memories = len(self._memory)

            self._stats.active_tokens += token_count

            await self._enforce_limits()

            return memory.memory_id

    # ========================================================
    # CONTEXT RETRIEVAL
    # ========================================================

    async def get_context_window(
        self,
        max_tokens: Optional[int] = None,
    ) -> List[MemoryEntry]:
        """
        Retrieve token-aware context window.
        """

        async with self._lock:

            budget = max_tokens or self.max_tokens

            sorted_entries = sorted(
                self._memory,
                key=self._priority_function,
                reverse=True,
            )

            selected: List[MemoryEntry] = []

            current_tokens = 0

            for memory in sorted_entries:

                if current_tokens + memory.token_count > budget:
                    continue

                memory.touch()

                selected.append(memory)

                current_tokens += memory.token_count

            return selected

    # ========================================================
    # EXECUTION TRACKING
    # ========================================================

    async def track_execution_state(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Track runtime execution state.
        """

        async with self._lock:

            self._execution_state[key] = value

    async def get_execution_state(
        self,
    ) -> Dict[str, Any]:
        """
        Retrieve execution state.
        """

        async with self._lock:

            return dict(self._execution_state)

    # ========================================================
    # SNAPSHOT MANAGEMENT
    # ========================================================

    async def create_snapshot(
        self,
    ) -> ExecutionSnapshot:
        """
        Create execution snapshot.
        """

        async with self._lock:

            snapshot = ExecutionSnapshot(
                snapshot_id=str(uuid.uuid4()),
                session_id=self.session_id,
                created_at=time.time(),
                memory_entries=[
                    asdict(memory)
                    for memory in self._memory
                ],
                execution_state=dict(
                    self._execution_state
                ),
            )

            self._stats.snapshot_count += 1

            return snapshot

    async def restore_snapshot(
        self,
        snapshot: ExecutionSnapshot,
    ) -> None:
        """
        Restore execution snapshot.
        """

        async with self._lock:

            self._memory.clear()

            for entry in snapshot.memory_entries:

                self._memory.append(
                    MemoryEntry(**entry)
                )

            self._execution_state = dict(
                snapshot.execution_state
            )

            self._recalculate_stats()

    # ========================================================
    # MEMORY LIMIT ENFORCEMENT
    # ========================================================

    async def _enforce_limits(
        self,
    ) -> None:
        """
        Enforce token and entry constraints.
        """

        while (
            self._stats.active_tokens
            > self.max_tokens
            or len(self._memory)
            > self.max_entries
        ):

            lowest_priority = min(
                self._memory,
                key=self._priority_function,
            )

            self._memory.remove(lowest_priority)

            self._stats.total_evictions += 1

            self._stats.active_tokens -= (
                lowest_priority.token_count
            )

            self._stats.total_memories = len(
                self._memory
            )

    # ========================================================
    # PRIORITIZATION
    # ========================================================

    @staticmethod
    def _priority_function(
        memory: MemoryEntry,
    ) -> float:
        """
        Memory prioritization scoring.
        """

        recency_score = (
            time.time() - memory.created_at
        )

        access_score = (
            memory.access_count * 0.2
        )

        return (
            memory.priority_score * 0.4
            + memory.relevance_score * 0.3
            + access_score
            - recency_score * 0.0001
        )

    # ========================================================
    # MEMORY CLEARING
    # ========================================================

    async def clear(
        self,
    ) -> None:
        """
        Clear working memory.
        """

        async with self._lock:

            self._memory.clear()

            self._execution_state.clear()

            self._recalculate_stats()

    # ========================================================
    # STATS
    # ========================================================

    def get_stats(
        self,
    ) -> WorkingMemoryStats:
        """
        Retrieve working memory statistics.
        """

        return self._stats

    def _recalculate_stats(
        self,
    ) -> None:
        """
        Recalculate runtime statistics.
        """

        self._stats.total_memories = len(
            self._memory
        )

        self._stats.active_tokens = sum(
            memory.token_count
            for memory in self._memory
        )

    # ========================================================
    # DEBUGGING
    # ========================================================

    async def dump_memory(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Export memory for debugging.
        """

        async with self._lock:

            return [
                asdict(memory)
                for memory in self._memory
            ]
