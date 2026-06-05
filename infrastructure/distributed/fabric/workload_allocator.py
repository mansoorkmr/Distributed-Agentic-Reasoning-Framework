"""
DARF Workload Allocator
=======================

Distributed Agentic Reasoning Framework

Responsibilities
----------------
- Resource admission control
- CPU allocation
- GPU allocation
- Memory allocation
- Resource reservation
- Capacity tracking
- Allocation lifecycle management
- Cluster utilization monitoring
"""

from __future__ import annotations

import asyncio
import time
import uuid

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Dict
from typing import Optional
from typing import Any


# ============================================================
# ALLOCATION STRATEGY
# ============================================================


class AllocationStrategy(str, Enum):

    BEST_FIT = "best_fit"

    FIRST_FIT = "first_fit"

    BALANCED = "balanced"

    GPU_PREFERRED = "gpu_preferred"

    CPU_PREFERRED = "cpu_preferred"

    MEMORY_PREFERRED = "memory_preferred"


# ============================================================
# RESOURCE REQUEST
# ============================================================


@dataclass(slots=True)
class ResourceRequest:

    request_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    cpu_cores: float = 1.0

    gpu_count: int = 0

    memory_gb: float = 1.0

    estimated_runtime_seconds: int = 300

    priority: int = 0

    exclusive: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# RESOURCE ALLOCATION
# ============================================================


@dataclass(slots=True)
class ResourceAllocation:

    allocation_id: str

    node_id: str

    request_id: str

    allocated_cpu: float

    allocated_gpu: int

    allocated_memory: float

    created_at: float

    expires_at: Optional[float]


# ============================================================
# NODE CAPACITY
# ============================================================


@dataclass(slots=True)
class NodeCapacity:

    node_id: str

    total_cpu: float

    total_gpu: int

    total_memory_gb: float

    used_cpu: float = 0.0

    used_gpu: int = 0

    used_memory_gb: float = 0.0

    # --------------------------------------------------------

    @property
    def available_cpu(self) -> float:

        return max(
            self.total_cpu - self.used_cpu,
            0.0,
        )

    @property
    def available_gpu(self) -> int:

        return max(
            self.total_gpu - self.used_gpu,
            0,
        )

    @property
    def available_memory(self) -> float:

        return max(
            self.total_memory_gb
            - self.used_memory_gb,
            0.0,
        )

    @property
    def cpu_utilization(self) -> float:

        if self.total_cpu <= 0:
            return 0.0

        return self.used_cpu / self.total_cpu

    @property
    def gpu_utilization(self) -> float:

        if self.total_gpu <= 0:
            return 0.0

        return self.used_gpu / self.total_gpu

    @property
    def memory_utilization(self) -> float:

        if self.total_memory_gb <= 0:
            return 0.0

        return (
            self.used_memory_gb
            / self.total_memory_gb
        )


# ============================================================
# ALLOCATION METRICS
# ============================================================


@dataclass(slots=True)
class AllocationMetrics:

    allocations_granted: int = 0

    allocations_denied: int = 0

    resources_reserved: int = 0

    resources_released: int = 0

    active_allocations: int = 0


# ============================================================
# WORKLOAD ALLOCATOR
# ============================================================


class WorkloadAllocator:
    """
    Central resource allocator.

    Single source of truth for
    resource reservations.
    """

    MAX_NODE_UTILIZATION = 0.90

    def __init__(self) -> None:

        self._nodes: Dict[
            str,
            NodeCapacity,
        ] = {}

        self._allocations: Dict[
            str,
            ResourceAllocation,
        ] = {}

        self._metrics = AllocationMetrics()

        self._lock = asyncio.Lock()

    # ========================================================
    # NODE REGISTRATION
    # ========================================================

    async def register_node(
        self,
        node: NodeCapacity,
    ) -> None:

        async with self._lock:

            self._nodes[node.node_id] = node

    # ========================================================
    # CAPACITY LOOKUP
    # ========================================================

    async def get_node_capacity(
        self,
        node_id: str,
    ) -> Optional[NodeCapacity]:

        return self._nodes.get(node_id)

    # ========================================================
    # VALIDATION
    # ========================================================

    def can_allocate(
        self,
        node: NodeCapacity,
        request: ResourceRequest,
    ) -> bool:

        if (
            node.available_cpu
            < request.cpu_cores
        ):
            return False

        if (
            node.available_gpu
            < request.gpu_count
        ):
            return False

        if (
            node.available_memory
            < request.memory_gb
        ):
            return False

        projected_cpu = (
            node.used_cpu
            + request.cpu_cores
        ) / node.total_cpu

        projected_memory = (
            node.used_memory_gb
            + request.memory_gb
        ) / node.total_memory_gb

        if (
            projected_cpu
            > self.MAX_NODE_UTILIZATION
        ):
            return False

        if (
            projected_memory
            > self.MAX_NODE_UTILIZATION
        ):
            return False

        return True

    # ========================================================
    # NODE SCORING
    # ========================================================

    def score_node(
        self,
        node: NodeCapacity,
        strategy: AllocationStrategy,
    ) -> float:

        cpu_headroom = (
            node.available_cpu
            / max(node.total_cpu, 1)
        )

        memory_headroom = (
            node.available_memory
            / max(
                node.total_memory_gb,
                1,
            )
        )

        gpu_headroom = (
            node.available_gpu
            / max(node.total_gpu, 1)
            if node.total_gpu > 0
            else 0.0
        )

        if (
            strategy
            == AllocationStrategy.CPU_PREFERRED
        ):
            return cpu_headroom

        if (
            strategy
            == AllocationStrategy.GPU_PREFERRED
        ):
            return gpu_headroom

        if (
            strategy
            == AllocationStrategy.MEMORY_PREFERRED
        ):
            return memory_headroom

        return (
            cpu_headroom * 0.40
            + memory_headroom * 0.40
            + gpu_headroom * 0.20
        )

    # ========================================================
    # ALLOCATION
    # ========================================================

    async def allocate(
        self,
        request: ResourceRequest,
        strategy: AllocationStrategy = (
            AllocationStrategy.BALANCED
        ),
    ) -> ResourceAllocation:

        async with self._lock:

            candidates = []

            for node in self._nodes.values():

                if not self.can_allocate(
                    node,
                    request,
                ):
                    continue

                score = self.score_node(
                    node,
                    strategy,
                )

                candidates.append(
                    (score, node)
                )

            if not candidates:

                self._metrics.allocations_denied += 1

                raise RuntimeError(
                    "No node has sufficient resources."
                )

            candidates.sort(
                key=lambda x: x[0],
                reverse=True,
            )

            selected_node = candidates[0][1]

            selected_node.used_cpu += (
                request.cpu_cores
            )

            selected_node.used_gpu += (
                request.gpu_count
            )

            selected_node.used_memory_gb += (
                request.memory_gb
            )

            allocation = ResourceAllocation(
                allocation_id=str(
                    uuid.uuid4()
                ),
                node_id=selected_node.node_id,
                request_id=request.request_id,
                allocated_cpu=request.cpu_cores,
                allocated_gpu=request.gpu_count,
                allocated_memory=request.memory_gb,
                created_at=time.time(),
                expires_at=(
                    time.time()
                    + request.estimated_runtime_seconds
                ),
            )

            self._allocations[
                allocation.allocation_id
            ] = allocation

            self._metrics.allocations_granted += 1

            self._metrics.resources_reserved += 1

            self._metrics.active_allocations += 1

            return allocation

    # ========================================================
    # RELEASE
    # ========================================================

    async def release(
        self,
        allocation_id: str,
    ) -> bool:

        async with self._lock:

            allocation = (
                self._allocations.get(
                    allocation_id
                )
            )

            if allocation is None:
                return False

            node = self._nodes.get(
                allocation.node_id
            )

            if node is not None:

                node.used_cpu -= (
                    allocation.allocated_cpu
                )

                node.used_gpu -= (
                    allocation.allocated_gpu
                )

                node.used_memory_gb -= (
                    allocation.allocated_memory
                )

                node.used_cpu = max(
                    node.used_cpu,
                    0.0,
                )

                node.used_gpu = max(
                    node.used_gpu,
                    0,
                )

                node.used_memory_gb = max(
                    node.used_memory_gb,
                    0.0,
                )

            del self._allocations[
                allocation_id
            ]

            self._metrics.resources_released += 1

            self._metrics.active_allocations -= 1

            return True

    # ========================================================
    # ALLOCATION LOOKUP
    # ========================================================

    async def get_allocation(
        self,
        allocation_id: str,
    ) -> Optional[ResourceAllocation]:

        return self._allocations.get(
            allocation_id
        )

    # ========================================================
    # CLUSTER SUMMARY
    # ========================================================

    async def cluster_capacity(
        self,
    ) -> Dict[str, float]:

        total_cpu = sum(
            n.total_cpu
            for n in self._nodes.values()
        )

        total_gpu = sum(
            n.total_gpu
            for n in self._nodes.values()
        )

        total_memory = sum(
            n.total_memory_gb
            for n in self._nodes.values()
        )

        used_cpu = sum(
            n.used_cpu
            for n in self._nodes.values()
        )

        used_gpu = sum(
            n.used_gpu
            for n in self._nodes.values()
        )

        used_memory = sum(
            n.used_memory_gb
            for n in self._nodes.values()
        )

        return {
            "total_cpu": total_cpu,
            "used_cpu": used_cpu,
            "total_gpu": total_gpu,
            "used_gpu": used_gpu,
            "total_memory_gb": total_memory,
            "used_memory_gb": used_memory,
        }

    # ========================================================
    # METRICS
    # ========================================================

    def get_metrics(
        self,
    ) -> AllocationMetrics:

        return self._metrics

    # ========================================================
    # HEALTH
    # ========================================================

    async def health_check(
        self,
    ) -> Dict[str, Any]:

        return {
            "status": "healthy",
            "registered_nodes": len(
                self._nodes
            ),
            "active_allocations": (
                self._metrics.active_allocations
            ),
            "allocations_granted": (
                self._metrics.allocations_granted
            ),
            "allocations_denied": (
                self._metrics.allocations_denied
            ),
        }
