"""
Distributed Agentic Reasoning Framework (DARF)

Persistence Store

Purpose
-------
Persistent storage backend for memory.

Responsibilities
----------------
- Save memories
- Load memories
- Delete memories
- Clear persistent storage

Current backend:
JSON

Future backends:
SQLite
PostgreSQL
Redis
MongoDB
"""
from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class PersistenceStore:
    file_path: str = "memory_store.json"
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    def save(self, data: Dict[str, Any]) -> None:
        Path(self.file_path).write_text(
            json.dumps(
                data,
                indent=4,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    def load(self) -> Dict[str, Any]:
        path = Path(self.file_path)
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def exists(self) -> bool:
        return Path(self.file_path).exists()

    def delete(self) -> None:
        path = Path(self.file_path)
        if path.exists():
            path.unlink()

    def clear(self) -> None:
        self.save({})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "exists": self.exists(),
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
        return f"PersistenceStore({self.file_path})"

    def __repr__(self) -> str:
        return f"<PersistenceStore path='{self.file_path}'>"