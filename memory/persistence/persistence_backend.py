"""
Distributed Agentic Reasoning Framework (DARF)

Persistence Backend

Purpose
-------
Abstract persistence backend.

Current implementation:
JSON backend.

Future implementations:
- SQLite
- PostgreSQL
- Redis
- MongoDB
- S3
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict

from memory.persistence.persistence_store import PersistenceStore


@dataclass(slots=True)
class PersistenceBackend:
    store: PersistenceStore = field(default_factory=PersistenceStore)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    def save_memory(self, data: Dict[str, Any]) -> None:
        self.store.save(data)

    def load_memory(self) -> Dict[str, Any]:
        return self.store.load()

    def exists(self) -> bool:
        return self.store.exists()

    def delete_memory(self) -> None:
        self.store.delete()

    def clear(self) -> None:
        self.store.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "store": self.store.to_dict(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            indent=4,
            sort_keys=True,
        )

    def __str__(self) -> str:
        return "PersistenceBackend"

    def __repr__(self) -> str:
        return "<PersistenceBackend>"