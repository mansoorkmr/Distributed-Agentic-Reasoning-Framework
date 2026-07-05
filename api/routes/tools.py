"""
Distributed Agentic Reasoning Framework (DARF)

Tools Route
"""

from __future__ import annotations

from fastapi import APIRouter

from agents.tool_agent import ToolAgent
from api.models.response import (
    ToolResponse,
    ToolInfo,
)

router = APIRouter(
    prefix="/tools",
    tags=["Tools"],
)

# ============================================================
# SHARED TOOL AGENT
# ============================================================

_tool_agent = ToolAgent()

# ============================================================
# GET /tools
# ============================================================

@router.get(
    "",
    response_model=ToolResponse,
)
def get_tools():
    return ToolResponse(
        success=True,
        message="Registered tools.",
        count=_tool_agent.tool_count(),
        capabilities=_tool_agent.get_capabilities(),
        tools=[
            ToolInfo(
                name=name,
                status="Ready",
                category="Execution",
            )
            for name in _tool_agent.tool_names()
        ],
    )