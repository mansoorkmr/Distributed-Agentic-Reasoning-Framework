"""
Distributed Agentic Reasoning Framework (DARF)
Execution Fabric

Resource Manager

Purpose
-------
Defines the canonical resource manager used by the
DARF Execution Fabric.

The resource manager tracks allocatable execution
resources and validates allocation requests.

Responsibilities
----------------
- Resource accounting
- Allocation
- Release
- Capacity validation
- Future distributed resource support

Design Principles
-----------------
- Thread-safe design
- Strong typing
- Backend agnostic
- Deterministic accounting

Thread Safety
-------------
Thread-safe when externally synchronized.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Dict


# ============================================================
# RESOURCE MANAGER
# ============================================================


@dataclass(slots=True)
class ResourceManager:
    """
    Canonical execution resource manager.
    """

    total_slots: int = 1

    allocated_slots: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    version: str = "1.0"

    def __post_init__(
        self,
    ) -> None:
        """
        Validate configuration.
        """

        if self.total_slots <= 0:
            raise ValueError(
                "total_slots must be > 0."
            )

        if self.allocated_slots < 0:
            raise ValueError(
                "allocated_slots must be >= 0."
            )

        if (
            self.allocated_slots
            > self.total_slots
        ):
            raise ValueError(
                "allocated_slots cannot exceed total_slots."
            )
            # ========================================================
    # RESOURCE OPERATIONS
    # ========================================================

    def allocate(
        self,
        slots: int = 1,
    ) -> bool:
        """
        Allocate execution slots.

        Returns
        -------
        bool
            True if allocation succeeded.
        """

        if slots <= 0:
            raise ValueError(
                "slots must be > 0."
            )

        if (
            self.available_slots()
            < slots
        ):
            return False

        self.allocated_slots += slots

        return True

    def release(
        self,
        slots: int = 1,
    ) -> None:
        """
        Release allocated slots.
        """

        if slots <= 0:
            raise ValueError(
                "slots must be > 0."
            )

        if slots > self.allocated_slots:
            raise ValueError(
                "Cannot release more slots than allocated."
            )

        self.allocated_slots -= slots

    def reset(
        self,
    ) -> None:
        """
        Reset all allocations.
        """

        self.allocated_slots = 0
            # ========================================================
    # RESOURCE STATUS
    # ========================================================

    def available_slots(
        self,
    ) -> int:
        """
        Return available execution slots.
        """

        return (
            self.total_slots
            - self.allocated_slots
        )

    def has_capacity(
        self,
        slots: int = 1,
    ) -> bool:
        """
        Determine whether sufficient
        capacity exists.
        """

        return (
            self.available_slots()
            >= slots
        )

    def utilization(
        self,
    ) -> float:
        """
        Return resource utilization.
        """

        return round(
            self.allocated_slots
            / self.total_slots,
            6,
        )
        # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Serialize resource manager.
        """

        return {
            "total_slots": self.total_slots,
            "allocated_slots": self.allocated_slots,
            "available_slots": self.available_slots(),
            "utilization": self.utilization(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(
        self,
    ) -> str:
        """
        Serialize to JSON.
        """

        import json

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
        """
        Human-readable representation.
        """

        return (
            f"{self.allocated_slots}/"
            f"{self.total_slots}"
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"<ResourceManager "
            f"allocated={self.allocated_slots} "
            f"total={self.total_slots}>"
        )
    