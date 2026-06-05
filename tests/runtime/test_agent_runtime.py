"""
DARF Agent Runtime Integration Tests
"""

from __future__ import annotations

import asyncio

from agents.base_agent import (
    BaseAgent,
    AgentContext,
)

from agents.runtime.agent_runtime import (
    AgentRuntime,
    AgentExecutionRequest,
)
# ============================================================
# TEST AGENTS
# ============================================================


class SuccessfulAgent(BaseAgent):
    """
    Deterministic success agent.
    """

    def __init__(self) -> None:

        super().__init__(
            "successful_agent"
        )

    def _execute_impl(
        self,
        task: str,
        context: AgentContext,
    ) -> str:

        return (
            f"processed:{task}"
        )


class FailingAgent(BaseAgent):
    """
    Deterministic failure agent.
    """

    def __init__(self) -> None:

        super().__init__(
            "failing_agent"
        )

    def _execute_impl(
        self,
        task: str,
        context: AgentContext,
    ) -> str:

        raise RuntimeError(
            "intentional_test_failure"
        )
# ============================================================
# HELPERS
# ============================================================


def build_request(
    agent_id: str,
    task: str = "test-task",
) -> AgentExecutionRequest:

    return AgentExecutionRequest(
        agent_id=agent_id,
        task=task,
        metadata={},
    )
# ============================================================
# REGISTRATION TESTS
# ============================================================


async def test_registration() -> None:

    runtime = AgentRuntime()

    await runtime.register_agent(
        "success",
        SuccessfulAgent(),
    )

    agent = await runtime.get_agent(
        "success"
    )

    assert agent is not None


async def test_listing() -> None:

    runtime = AgentRuntime()

    await runtime.register_agent(
        "success",
        SuccessfulAgent(),
    )

    agents = await runtime.list_agents()

    assert (
        "success"
        in agents
    )


async def test_unregister() -> None:

    runtime = AgentRuntime()

    await runtime.register_agent(
        "success",
        SuccessfulAgent(),
    )

    await runtime.unregister_agent(
        "success"
    )

    agents = await runtime.list_agents()

    assert (
        "success"
        not in agents
    )
# ============================================================
# EXECUTION TESTS
# ============================================================


async def test_successful_execution() -> None:

    runtime = AgentRuntime()

    await runtime.register_agent(
        "success",
        SuccessfulAgent(),
    )

    result = await runtime.execute(
        build_request(
            "success",
            "hello",
        )
    )

    assert result.success

    assert (
        result.output
        == "processed:hello"
    )


async def test_failed_execution() -> None:

    runtime = AgentRuntime()

    await runtime.register_agent(
        "failure",
        FailingAgent(),
    )

    result = await runtime.execute(
        build_request(
            "failure",
            "hello",
        )
    )

    assert result.success is False

    assert (
        result.error_message
        is not None
    )
# ============================================================
# HEALTH TESTS
# ============================================================


async def test_health_check() -> None:

    runtime = AgentRuntime()

    await runtime.register_agent(
        "success",
        SuccessfulAgent(),
    )

    health = await runtime.health_check()

    assert (
        health["status"]
        == "healthy"
    )

    assert (
        "metrics"
        in health
    )

    assert (
        "registry"
        in health
    )

    assert (
        "lifecycle"
        in health
    )
# ============================================================
# CONCURRENCY TESTS
# ============================================================


async def test_concurrent_execution() -> None:

    runtime = AgentRuntime()

    # Register independent agents
    # to validate runtime concurrency
    # without violating lifecycle rules.

    for i in range(20):

        await runtime.register_agent(
            f"success_{i}",
            SuccessfulAgent(),
        )

    tasks = []

    for i in range(20):

        tasks.append(
            runtime.execute(
                build_request(
                    f"success_{i}",
                    f"task-{i}",
                )
            )
        )

    results = await asyncio.gather(
        *tasks
    )

    assert len(results) == 20

    assert all(
        result.success
        for result in results
    )

    metrics = runtime.get_metrics()

    assert (
        metrics.executions_started
        == 20
    )

    assert (
        metrics.executions_completed
        == 20
    )

    assert (
        metrics.executions_failed
        == 0
    )

    assert (
        metrics.registered_agents
        == 20
    )
# ============================================================
# RUNNER
# ============================================================


async def run_suite() -> None:

    print(
        "\n========================================"
    )

    print(
        "DARF AGENT RUNTIME TEST"
    )

    print(
        "========================================\n"
    )

    await test_registration()
    print("[PASS] registration")

    await test_listing()
    print("[PASS] listing")

    await test_unregister()
    print("[PASS] unregister")

    await test_successful_execution()
    print("[PASS] successful_execution")

    await test_failed_execution()
    print("[PASS] failed_execution")

    await test_health_check()
    print("[PASS] health_check")

    await test_concurrent_execution()
    print("[PASS] concurrent_execution")

    print(
        "\n========================================"
    )

    print(
        "ALL RUNTIME TESTS PASSED"
    )

    print(
        "========================================"
    )


async def main() -> None:

    await run_suite()


if __name__ == "__main__":

    asyncio.run(main())
