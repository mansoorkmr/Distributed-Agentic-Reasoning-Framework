"""
Institutional-Grade Episodic Memory System
==========================================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities:
- Long-term execution memory
- Historical workflow tracking
- Execution lineage
- Agent interaction history
- Runtime event persistence
- Reflective reasoning support
- Session archival
- Distributed cognitive continuity
"""

from __future__ import annotations

import asyncio
import json
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


# ============================================================
# EPISODIC EVENT
# ============================================================


@dataclass(slots=True)
class EpisodicEvent:
    """
    Represents a persistent execution event.
    """

    event_id: str

    session_id: str

    agent_id: str

    event_type: str

    content: Dict[str, Any]

    created_at: float = field(
        default_factory=time.time
    )

    importance_score: float = 1.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# EXECUTION LINEAGE
# ============================================================


@dataclass(slots=True)
class ExecutionLineage:
    """
    Represents execution ancestry.
    """

    lineage_id: str

    parent_event_id: Optional[str]

    child_event_ids: List[str]

    created_at: float = field(
        default_factory=time.time
    )


# ============================================================
# EPISODIC MEMORY STATS
# ============================================================


@dataclass(slots=True)
class EpisodicMemoryStats:
    """
    Episodic memory statistics.
    """

    total_events: int = 0

    archived_sessions: int = 0

    lineage_count: int = 0

    retrieval_operations: int = 0


# ============================================================
# EPISODIC MEMORY ENGINE
# ============================================================


class EpisodicMemory:
    """
    Institutional-grade episodic memory engine.

    Features:
    - Persistent execution memory
    - Session archival
    - Historical retrieval
    - Event lineage tracking
    - Reflective cognition support
    - Distributed-safe persistence
    """

    def __init__(
        self,
        storage_path: str = "memory/episodic",
    ) -> None:

        self.storage_path = Path(storage_path)

        self.storage_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._events: Dict[
            str,
            EpisodicEvent,
        ] = {}

        self._lineages: Dict[
            str,
            ExecutionLineage,
        ] = {}

        self._stats = EpisodicMemoryStats()

        self._lock = asyncio.Lock()

    # ========================================================
    # EVENT STORAGE
    # ========================================================

    async def store_event(
        self,
        session_id: str,
        agent_id: str,
        event_type: str,
        content: Dict[str, Any],
        importance_score: float = 1.0,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> str:
        """
        Store execution event.
        """

        async with self._lock:

            event = EpisodicEvent(
                event_id=str(uuid.uuid4()),
                session_id=session_id,
                agent_id=agent_id,
                event_type=event_type,
                content=content,
                importance_score=importance_score,
                metadata=metadata or {},
            )

            self._events[event.event_id] = event

            self._stats.total_events += 1

            await self._persist_event(event)

            return event.event_id

    # ========================================================
    # EVENT RETRIEVAL
    # ========================================================

    async def get_event(
        self,
        event_id: str,
    ) -> Optional[EpisodicEvent]:
        """
        Retrieve event by ID.
        """

        async with self._lock:

            self._stats.retrieval_operations += 1

            return self._events.get(event_id)

    async def get_session_events(
        self,
        session_id: str,
    ) -> List[EpisodicEvent]:
        """
        Retrieve session history.
        """

        async with self._lock:

            self._stats.retrieval_operations += 1

            return sorted(
                [
                    event
                    for event in self._events.values()
                    if event.session_id
                    == session_id
                ],
                key=lambda event: (
                    event.created_at
                ),
            )

    async def search_events(
        self,
        query: str,
    ) -> List[EpisodicEvent]:
        """
        Simple semantic-like search.
        """

        async with self._lock:

            results = []

            query = query.lower()

            for event in self._events.values():

                content = json.dumps(
                    event.content
                ).lower()

                if query in content:

                    results.append(event)

            return sorted(
                results,
                key=lambda event: (
                    event.importance_score
                ),
                reverse=True,
            )

    # ========================================================
    # LINEAGE TRACKING
    # ========================================================

    async def create_lineage(
        self,
        parent_event_id: Optional[str],
        child_event_ids: List[str],
    ) -> str:
        """
        Create execution lineage.
        """

        async with self._lock:

            lineage = ExecutionLineage(
                lineage_id=str(uuid.uuid4()),
                parent_event_id=parent_event_id,
                child_event_ids=child_event_ids,
            )

            self._lineages[
                lineage.lineage_id
            ] = lineage

            self._stats.lineage_count += 1

            return lineage.lineage_id

    async def get_lineage(
        self,
        lineage_id: str,
    ) -> Optional[ExecutionLineage]:
        """
        Retrieve lineage.
        """

        async with self._lock:

            return self._lineages.get(
                lineage_id
            )

    # ========================================================
    # SESSION ARCHIVAL
    # ========================================================

    async def archive_session(
        self,
        session_id: str,
    ) -> Path:
        """
        Archive session to disk.
        """

        async with self._lock:

            events = await self.get_session_events(
                session_id
            )

            archive_path = (
                self.storage_path
                / f"{session_id}.json"
            )

            payload = [
                asdict(event)
                for event in events
            ]

            with open(
                archive_path,
                "w",
                encoding="utf-8",
            ) as archive_file:

                json.dump(
                    payload,
                    archive_file,
                    indent=2,
                )

            self._stats.archived_sessions += 1

            return archive_path

    # ========================================================
    # PERSISTENCE
    # ========================================================

    async def _persist_event(
        self,
        event: EpisodicEvent,
    ) -> None:
        """
        Persist event incrementally.
        """

        session_dir = (
            self.storage_path
            / event.session_id
        )

        session_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        event_path = (
            session_dir
            / f"{event.event_id}.json"
        )

        with open(
            event_path,
            "w",
            encoding="utf-8",
        ) as event_file:

            json.dump(
                asdict(event),
                event_file,
                indent=2,
            )

    # ========================================================
    # REFLECTION SUPPORT
    # ========================================================

    async def get_high_importance_events(
        self,
        threshold: float = 0.8,
    ) -> List[EpisodicEvent]:
        """
        Retrieve high-importance memories.
        """

        async with self._lock:

            return sorted(
                [
                    event
                    for event in self._events.values()
                    if event.importance_score
                    >= threshold
                ],
                key=lambda event: (
                    event.importance_score
                ),
                reverse=True,
            )

    # ========================================================
    # STATISTICS
    # ========================================================

    def get_stats(
        self,
    ) -> EpisodicMemoryStats:
        """
        Retrieve runtime statistics.
        """

        return self._stats

    # ========================================================
    # DEBUGGING
    # ========================================================

    async def dump_events(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Export all events.
        """

        async with self._lock:

            return [
                asdict(event)
                for event in self._events.values()
            ]
