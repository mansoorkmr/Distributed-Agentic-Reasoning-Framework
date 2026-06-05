"""
DARF Agent Registry Integration Test

Validates:

- Registration
- Duplicate protection
- Lookup
- Existence
- Listing
- Lifecycle synchronization
- Unregistration
- Snapshot generation
- Health reporting
"""

from __future__ import annotations

import asyncio

from agents.base_agent import (
    BaseAgent,
    AgentContext,
)

from agents.runtime.agent_registry import (
    AgentRegistry,
)

from agents.runtime.exceptions import (
    AgentAlreadyRegisteredError,
    AgentNotFoundError,
)


# ============================================================
# TEST AGENT
# ============================================================


class TestAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            "test-agent"
        )

    def _execute_impl(
        self,
        task: str,
        context: AgentContext,
    ) -> str:

        return f"processed:{task}"


# ============================================================
# TESTS
# ============================================================


async def test_registration():

    registry = AgentRegistry()

    agent = TestAgent()

    await registry.register_agent(
        "agent-1",
        agent,
    )

    assert registry.exists(
        "agent-1"
    )

    assert (
        registry.count()
        == 1
    )

    print(
        "[PASS] registration"
    )


async def test_duplicate_registration():

    registry = AgentRegistry()

    agent = TestAgent()

    await registry.register_agent(
        "agent-1",
        agent,
    )

    try:

        await registry.register_agent(
            "agent-1",
            agent,
        )

    except AgentAlreadyRegisteredError:

        print(
            "[PASS] duplicate_registration"
        )

        return

    raise AssertionError(
        "Duplicate registration allowed"
    )


async def test_lookup():

    registry = AgentRegistry()

    agent = TestAgent()

    await registry.register_agent(
        "agent-1",
        agent,
    )

    fetched = registry.get_agent(
        "agent-1"
    )

    assert fetched is agent

    print(
        "[PASS] lookup"
    )


async def test_listing():

    registry = AgentRegistry()

    await registry.register_agent(
        "agent-a",
        TestAgent(),
    )

    await registry.register_agent(
        "agent-b",
        TestAgent(),
    )

    agents = registry.list_agents()

    assert len(
        agents
    ) == 2

    print(
        "[PASS] listing"
    )


async def test_snapshot():

    registry = AgentRegistry()

    await registry.register_agent(
        "agent-1",
        TestAgent(),
    )

    snapshot = (
        await registry.snapshot()
    )

    assert (
        snapshot[
            "registered_agents"
        ]
        == 1
    )

    print(
        "[PASS] snapshot"
    )


async def test_health():

    registry = AgentRegistry()

    await registry.register_agent(
        "agent-1",
        TestAgent(),
    )

    health = (
        await registry.health_check()
    )

    assert (
        health["status"]
        == "healthy"
    )

    print(
        "[PASS] health"
    )


async def test_unregister():

    registry = AgentRegistry()

    await registry.register_agent(
        "agent-1",
        TestAgent(),
    )

    await registry.unregister_agent(
        "agent-1"
    )

    try:

        registry.get_agent(
            "agent-1"
        )

    except AgentNotFoundError:

        print(
            "[PASS] unregister"
        )

        return

    raise AssertionError(
        "Agent still exists"
    )


# ============================================================
# RUNNER
# ============================================================


async def run_suite():

    print(
        "\n========================================"
    )

    print(
        "DARF AGENT REGISTRY TEST"
    )

    print(
        "========================================\n"
    )

    await test_registration()

    await test_duplicate_registration()

    await test_lookup()

    await test_listing()

    await test_snapshot()

    await test_health()

    await test_unregister()

    print(
        "\n========================================"
    )

    print(
        "ALL REGISTRY TESTS PASSED"
    )

    print(
        "========================================"
    )


async def main():

    await run_suite()


if __name__ == "__main__":

    asyncio.run(main())
