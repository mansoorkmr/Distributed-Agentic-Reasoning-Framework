"""
DARF Application

Initializes the complete agent framework.
"""

from __future__ import annotations

from agents.agent_context import AgentContext
from agents.agent_manager import AgentManager

from agents.llm_agent import LLMAgent
from agents.memory_agent import MemoryAgent
from agents.planner_agent import PlannerAgent
from agents.tool_agent import ToolAgent

from llm.factory import ProviderFactory


class DARFApplication:
    """
    Central DARF application.
    """

    def __init__(self) -> None:

        self.context = AgentContext()

        self.manager = AgentManager()

        self.provider = ProviderFactory.create()

        self._register_agents()

    def _register_agents(self) -> None:

        llm = LLMAgent()

        llm.set_provider(
            self.provider,
        )

        self.manager.register(
            llm,
        )

        self.manager.register(
            PlannerAgent(),
        )

        self.manager.register(
            MemoryAgent(),
        )

        self.manager.register(
            ToolAgent(),
        )

    def get_manager(self) -> AgentManager:

        return self.manager

    def get_context(self) -> AgentContext:

        return self.context