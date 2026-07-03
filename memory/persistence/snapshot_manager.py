"""
Distributed Agentic Reasoning Framework (DARF)

Snapshot Manager

Purpose
-------
Creates and restores snapshots of memory.

Responsibilities
----------------
- Create snapshot
- Restore snapshot
- List snapshots
- Delete snapshots

Current backend:
JSON snapshots
"""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class SnapshotManager:
    snapshot_directory: str = "snapshots"
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    def create_snapshot(self, data: Dict[str, Any]) -> str:
        directory = Path(self.snapshot_directory)
        directory.mkdir(parents=True, exist_ok=True)

        filename = datetime.utcnow().strftime("%Y%m%d_%H%M%S") + ".json"
        path = directory / filename

        path.write_text(
            json.dumps(
                data,
                indent=4,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        return str(path)

    def restore_snapshot(self, snapshot_path: str) -> Dict[str, Any]:
        return json.loads(
            Path(snapshot_path).read_text(encoding="utf-8")
        )

    def list_snapshots(self) -> List[str]:
        directory = Path(self.snapshot_directory)
        
        if not directory.exists():
            return []

        return sorted(
            str(file)
            for file in directory.glob("*.json")
        )

    def delete_snapshot(self, snapshot_path: str) -> None:
        path = Path(snapshot_path)
        if path.exists():
            path.unlink()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_directory": self.snapshot_directory,
            "snapshot_count": len(self.list_snapshots()),
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
        return f"SnapshotManager({len(self.list_snapshots())} snapshots)"

    def __repr__(self) -> str:
        return f"<SnapshotManager count={len(self.list_snapshots())}>"