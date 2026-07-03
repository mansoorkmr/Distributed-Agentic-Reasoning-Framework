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

    return AgentsResponse(

        success=True,

        message="Registered agents.",

        agents=manager.names(),

    )