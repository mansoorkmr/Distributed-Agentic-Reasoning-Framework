"""
Distributed Agentic Reasoning Framework (DARF)

Runtime Configuration
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict


@dataclass(slots=True)
class RuntimeConfig:

    runtime_mode: str = "production"

    worker_threads: int = 4

    enable_logging: bool = True

    debug_mode: bool = False

    auto_recovery: bool = True

    startup_timeout: float = 30.0

    shutdown_timeout: float = 30.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------

    def production_mode(self) -> bool:

        return self.runtime_mode.lower() == "production"

    def debug_enabled(self) -> bool:

        return self.debug_mode

    def logging_enabled(self) -> bool:

        return self.enable_logging

    def recovery_enabled(self) -> bool:

        return self.auto_recovery

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:

        return {

            "runtime_mode": self.runtime_mode,

            "worker_threads": self.worker_threads,

            "enable_logging": self.enable_logging,

            "debug_mode": self.debug_mode,

            "auto_recovery": self.auto_recovery,

            "startup_timeout": self.startup_timeout,

            "shutdown_timeout": self.shutdown_timeout,

            "metadata": self.metadata,

            "version": self.version,

        }

    def to_json(self) -> str:

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(self) -> str:

        return (

            f"RuntimeConfig(mode={self.runtime_mode})"

        )

    def __repr__(self) -> str:

        return (

            "<RuntimeConfig "

            f"mode='{self.runtime_mode}' "

            f"workers={self.worker_threads}>"

        )