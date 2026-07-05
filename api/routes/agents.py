"""
Distributed Agentic Reasoning Framework (DARF)

Agents Route
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
)

from agents.agent_manager import AgentManager

from api.dependencies import (
    get_agent_manager,
)

from api.models.response import (
    AgentInfo,
    AgentsResponse,
)

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)

# ============================================================
# GET /agents
# ============================================================

@router.get(
    "",
    response_model=AgentsResponse,
)
def get_agents(
    manager: AgentManager = Depends(
        get_agent_manager,
    ),
):
    agents: list[AgentInfo] = []

    for agent in manager.agents():
        capabilities: list[str] = []

        if hasattr(agent, "get_capabilities"):
            capabilities = agent.get_capabilities()

        agents.append(
            AgentInfo(
                id=agent.agent_id,
                name=agent.name,
                description=agent.description,
                version=agent.version,
                status="Ready",
                capabilities=capabilities,
            )
        )

    return AgentsResponse(
        success=True,
        message="Registered agents.",
        count=len(agents),
        agents=agents,
    )