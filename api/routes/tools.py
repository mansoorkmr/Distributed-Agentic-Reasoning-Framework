"""
Distributed Agentic Reasoning Framework (DARF)

Tools Route
"""

from __future__ import annotations

from fastapi import APIRouter

from agents.tool_agent import ToolAgent

from api.models.response import APIResponse

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
)
def get_tools():

    return {

        "success": True,

        "message": "Registered tools.",

        "count": _tool_agent.tool_count(),

        "tools": _tool_agent.tool_names(),

    }