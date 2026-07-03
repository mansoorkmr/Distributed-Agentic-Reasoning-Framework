"""
Distributed Agentic Reasoning Framework (DARF)

Tool Agent

Purpose
-------
Provides the canonical execution agent for external
tools, APIs, services, and callable functions.

Responsibilities
----------------
- Execute registered tools
- Execute Python callables
- Execute external services
- Capture outputs
- Return AgentResult

Design Principles
-----------------
- Stateless execution
- Tool abstraction
- Safe execution
- Production-ready

Thread Safety
-------------
Thread-safe.

Author
------
Distributed Agentic Reasoning Framework (DARF)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from agents.base_agent import BaseAgent
from agents.agent_context import AgentContext

__all__ = ["ToolAgent"]

# ============================================================
# TOOL AGENT
# ============================================================

@dataclass(slots=True)
class ToolAgent(BaseAgent):
    """
    Canonical DARF Tool Agent.
    Orchestrates the execution of external callables and APIs.
    """

    # Override BaseAgent defaults natively to maintain perfect dataclass inheritance
    id: str = "tool"
    name: str = "Tool Agent"
    description: str = "Executes registered tools and external services."
    version: str = "1.0"

    tools: Dict[str, Callable[..., Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ========================================================
    # TOOL REGISTRY
    # ========================================================

    def register_tool(self, name: str, tool: Callable[..., Any]) -> None:
        """Register a callable tool."""
        if not callable(tool):
            raise TypeError("tool must be callable.")
        self.tools[name] = tool

    def unregister_tool(self, name: str) -> bool:
        """Remove a registered tool."""
        return self.tools.pop(name, None) is not None

    def get_tool(self, name: str) -> Optional[Callable[..., Any]]:
        """Return a registered tool."""
        return self.tools.get(name)

    def has_tool(self, name: str) -> bool:
        """Determine whether a tool is registered."""
        return name in self.tools

    # ========================================================
    # EXECUTION
    # ========================================================

    def execute_tool(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a registered tool directly by name."""
        tool = self.get_tool(name)
        if tool is None:
            raise ValueError(f"Unknown tool '{name}'.")
        return tool(*args, **kwargs)

    def run(self, context: AgentContext, **kwargs: Any) -> Any:
        """
        Execute a registered tool within the DARF context flow.
        """
        tool_name = kwargs.get("tool")
        if tool_name is None:
            raise ValueError("No tool specified.")

        tool_kwargs = kwargs.get("tool_kwargs", {})
        
        output = self.execute_tool(tool_name, **tool_kwargs)
        
        context.set_output(self.agent_id, output)
        return output

    # ========================================================
    # TOOL UTILITIES (Part 3 Implementation)
    # ========================================================

    def tool_count(self) -> int:
        """Return the number of registered tools."""
        return len(self.tools)

    def tool_names(self) -> List[str]:
        """Return the names of all registered tools."""
        return list(self.tools.keys())

    def clear_tools(self) -> None:
        """Remove all registered tools."""
        self.tools.clear()

    def tool_ready(self) -> bool:
        """Determine if the agent is ready to execute tools."""
        return True

    def get_capabilities(self) -> List[str]:
        """Return supported capabilities."""
        return [
            "tool_execution",
            "tool_registration",
            "python_callable_execution",
            "external_service_execution",
        ]

    def supports(self, capability: str) -> bool:
        """Determine whether a capability is supported."""
        return capability in self.get_capabilities()

    def reset(self) -> None:
        """Reset the agent's tools and metadata."""
        self.clear_tools()
        self.metadata.clear()

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the tool agent."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "tool_ready": self.tool_ready(),
            "tool_count": self.tool_count(),
            "tools": self.tool_names(),
            "supported_capabilities": self.get_capabilities(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self) -> str:
        """Serialize the tool agent to JSON."""
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"ToolAgent({self.tool_count()} tools)"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"<ToolAgent id='{self.agent_id}' tools={self.tool_count()}>"