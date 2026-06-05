"""
DARF Integration Test
=====================

Validates:

1. Execution Fabric startup
2. Allocator node registration
3. Task submission
4. Queue processing
5. Routing
6. Resource allocation
7. Execution completion
8. Metrics integrity
9. Health monitoring

Run:

python tests/integration/test_execution_fabric.py
"""

from __future__ import annotations

import asyncio
import inspect
import traceback

from infrastructure.distributed.fabric.execution_fabric import (
    ExecutionFabric,
)

from infrastructure.distributed.fabric.execution_queue import (
    QueuePriority,
)

from infrastructure.distributed.fabric.workload_allocator import (
    ResourceRequest,
    NodeCapacity,
)

from infrastructure.distributed.cluster_manager import (
    ClusterNode,
    NodeStatus,
)


# ============================================================
# HELPERS
# ============================================================


def print_banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_success(msg: str) -> None:
    print(f"[PASS] {msg}")


def print_failure(msg: str) -> None:
    print(f"[FAIL] {msg}")


# ============================================================
# CLUSTER NODE FACTORY
# ============================================================


def create_cluster_node() -> ClusterNode:
    """
    Build ClusterNode dynamically based on
    actual constructor signature.
    """

    signature = inspect.signature(
        ClusterNode
    )

    kwargs = {}

    for name in signature.parameters:

        if name == "node_id":
            kwargs[name] = "node-1"

        elif name == "hostname":
            kwargs[name] = "localhost"

        elif name == "status":
            kwargs[name] = NodeStatus.ACTIVE

        elif name == "cpu_capacity":
            kwargs[name] = 64

        elif name == "gpu_capacity":
            kwargs[name] = 4

        elif name == "memory_capacity_gb":
            kwargs[name] = 256

        elif name == "active_workloads":
            kwargs[name] = 0

    return ClusterNode(**kwargs)


# ============================================================
# MAIN TEST
# ============================================================


async def run_test() -> None:

    print_banner(
        "DARF EXECUTION FABRIC INTEGRATION TEST"
    )

    #
    # Fabric
    #

    fabric = ExecutionFabric()

    await fabric.start()

    print_success(
        "Execution fabric started"
    )

    #
    # Allocator node
    #

    capacity = NodeCapacity(
        node_id="node-1",
        total_cpu=64,
        total_gpu=4,
        total_memory_gb=256,
    )

    await fabric.allocator.register_node(
        capacity
    )

    print_success(
        "Allocator node registered"
    )

    #
    # Cluster node
    #

    cluster_node = create_cluster_node()

    print_success(
        "Cluster node created"
    )

    #
    # Resource request
    #

    request = ResourceRequest(
        cpu_cores=4,
        gpu_count=0,
        memory_gb=8,
        estimated_runtime_seconds=60,
    )

    print_success(
        "Resource request created"
    )

    #
    # Submit task
    #

    execution_id = await fabric.submit_task(
        task_id="integration-task",
        agent_id="reasoning-agent",
        payload={
            "query": "Hello DARF"
        },
        resource_request=request,
        priority=QueuePriority.NORMAL,
    )

    print_success(
        f"Task submitted: {execution_id}"
    )

    #
    # Process task
    #

    result = await fabric.process_next(
        nodes=[cluster_node]
    )

    print_success(
        "Task processed"
    )

    #
    # Metrics
    #

    metrics = fabric.get_metrics()

    #
    # Health
    #

    health = await fabric.health_check()

    #
    # Assertions
    #

    assert result is not None

    assert isinstance(
        result,
        dict,
    )

    assert (
        result.get("status")
        == "success"
    )

    assert (
        metrics.completed_tasks
        >= 1
    )

    assert (
        metrics.failed_tasks
        == 0
    )

    assert (
        health["status"]
        in (
            "running",
            "degraded",
        )
    )

    print_banner(
        "EXECUTION RESULT"
    )

    print(result)

    print_banner(
        "METRICS"
    )

    print(metrics)

    print_banner(
        "HEALTH"
    )

    print(health)

    print_banner(
        "ALL TESTS PASSED"
    )

    await fabric.stop()

    print_success(
        "Execution fabric stopped"
    )


# ============================================================
# ENTRYPOINT
# ============================================================


async def main() -> None:

    try:

        await run_test()

    except AssertionError as exc:

        print_failure(
            f"Assertion failed: {exc}"
        )

        raise

    except Exception as exc:

        print_failure(
            f"Unexpected error: {exc}"
        )

        traceback.print_exc()

        raise


if __name__ == "__main__":

    asyncio.run(main())
