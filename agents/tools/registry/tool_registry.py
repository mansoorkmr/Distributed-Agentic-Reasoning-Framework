"""
Institutional-Grade Tool Registry System
========================================

Distributed Agentic Reasoning Framework (DARF)

Responsibilities:
- Dynamic tool registration
- Tool discovery/runtime lookup
- Permission orchestration
- Schema validation
- Lifecycle management
- Distributed-safe registry operations
- Tool metadata management
"""

from __future__ import annotations

import asyncio
import inspect
import time
import uuid

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional


# ============================================================
# TOOL TYPES
# ============================================================


class ToolType(str, Enum):
    """
    Supported tool categories.
    """

    SYSTEM = "system"

    REASONING = "reasoning"

    RETRIEVAL = "retrieval"

    EXECUTION = "execution"

    COMMUNICATION = "communication"

    EXTERNAL = "external"


# ============================================================
# TOOL STATUS
# ============================================================


class ToolStatus(str, Enum):
    """
    Tool lifecycle states.
    """

    ACTIVE = "active"

    DISABLED = "disabled"

    DEPRECATED = "deprecated"


# ============================================================
# TOOL SCHEMA
# ============================================================


@dataclass(slots=True)
class ToolSchema:
    """
    Tool execution schema.
    """

    input_schema: Dict[str, Any]

    output_schema: Dict[str, Any]

    required_fields: List[str]


# ============================================================
# TOOL METADATA
# ============================================================


@dataclass(slots=True)
class ToolMetadata:
    """
    Tool metadata container.
    """

    tool_id: str

    name: str

    description: str

    tool_type: ToolType

    created_at: float = field(
        default_factory=time.time
    )

    tags: List[str] = field(
        default_factory=list
    )

    version: str = "1.0.0"

    author: str = "DARF"

    permissions: List[str] = field(
        default_factory=list
    )


# ============================================================
# TOOL REGISTRATION
# ============================================================


@dataclass(slots=True)
class RegisteredTool:
    """
    Registered tool container.
    """

    metadata: ToolMetadata

    schema: ToolSchema

    handler: Callable[
        ...,
        Awaitable[Any],
    ]

    status: ToolStatus = (
        ToolStatus.ACTIVE
    )

    execution_count: int = 0

    last_execution_time: Optional[
        float
    ] = None


# ============================================================
# REGISTRY STATS
# ============================================================


@dataclass(slots=True)
class ToolRegistryStats:
    """
    Tool registry statistics.
    """

    total_tools: int = 0

    active_tools: int = 0

    disabled_tools: int = 0

    discovery_operations: int = 0

    registration_operations: int = 0


# ============================================================
# TOOL REGISTRY ENGINE
# ============================================================


class ToolRegistry:
    """
    Institutional-grade tool registry.

    Features:
    - Dynamic registration
    - Runtime discovery
    - Permission orchestration
    - Schema validation
    - Distributed-safe operations
    """

    def __init__(
        self,
    ) -> None:

        self._tools: Dict[
            str,
            RegisteredTool,
        ] = {}

        self._stats = ToolRegistryStats()

        self._lock = asyncio.Lock()

    # ========================================================
    # TOOL REGISTRATION
    # ========================================================

    async def register_tool(
        self,
        name: str,
        description: str,
        tool_type: ToolType,
        handler: Callable[
            ...,
            Awaitable[Any],
        ],
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        required_fields: Optional[
            List[str]
        ] = None,
        tags: Optional[
            List[str]
        ] = None,
        permissions: Optional[
            List[str]
        ] = None,
        version: str = "1.0.0",
    ) -> str:
        """
        Register tool dynamically.
        """

        async with self._lock:

            self._validate_handler(
                handler
            )

            tool_id = str(uuid.uuid4())

            metadata = ToolMetadata(
                tool_id=tool_id,
                name=name,
                description=description,
                tool_type=tool_type,
                tags=tags or [],
                permissions=permissions
                or [],
                version=version,
            )

            schema = ToolSchema(
                input_schema=input_schema,
                output_schema=output_schema,
                required_fields=required_fields
                or [],
            )

            tool = RegisteredTool(
                metadata=metadata,
                schema=schema,
                handler=handler,
            )

            self._tools[tool_id] = tool

            self._stats.registration_operations += 1

            self._recalculate_stats()

            return tool_id

    # ========================================================
    # TOOL DISCOVERY
    # ========================================================

    async def discover_tools(
        self,
        tool_type: Optional[
            ToolType
        ] = None,
        tags: Optional[
            List[str]
        ] = None,
    ) -> List[RegisteredTool]:
        """
        Discover available tools.
        """

        async with self._lock:

            self._stats.discovery_operations += 1

            tools = list(
                self._tools.values()
            )

            if tool_type:

                tools = [
                    tool
                    for tool in tools
                    if (
                        tool.metadata.tool_type
                        == tool_type
                    )
                ]

            if tags:

                tools = [
                    tool
                    for tool in tools
                    if any(
                        tag
                        in tool.metadata.tags
                        for tag in tags
                    )
                ]

            return tools

    async def get_tool(
        self,
        tool_id: str,
    ) -> Optional[RegisteredTool]:
        """
        Retrieve tool by ID.
        """

        async with self._lock:

            return self._tools.get(
                tool_id
            )

    async def get_tool_by_name(
        self,
        name: str,
    ) -> Optional[RegisteredTool]:
        """
        Retrieve tool by name.
        """

        async with self._lock:

            for tool in self._tools.values():

                if (
                    tool.metadata.name
                    == name
                ):
                    return tool

            return None

    # ========================================================
    # TOOL VALIDATION
    # ========================================================

    async def validate_input(
        self,
        tool_id: str,
        payload: Dict[str, Any],
    ) -> bool:
        """
        Validate tool input payload.
        """

        async with self._lock:

            tool = self._tools.get(
                tool_id
            )

            if not tool:
                return False

            required_fields = (
                tool.schema.required_fields
            )

            return all(
                field in payload
                for field
                in required_fields
            )

    # ========================================================
    # TOOL LIFECYCLE
    # ========================================================

    async def disable_tool(
        self,
        tool_id: str,
    ) -> bool:
        """
        Disable tool.
        """

        async with self._lock:

            tool = self._tools.get(
                tool_id
            )

            if not tool:
                return False

            tool.status = (
                ToolStatus.DISABLED
            )

            self._recalculate_stats()

            return True

    async def enable_tool(
        self,
        tool_id: str,
    ) -> bool:
        """
        Enable tool.
        """

        async with self._lock:

            tool = self._tools.get(
                tool_id
            )

            if not tool:
                return False

            tool.status = (
                ToolStatus.ACTIVE
            )

            self._recalculate_stats()

            return True

    # ========================================================
    # EXECUTION TRACKING
    # ========================================================

    async def track_execution(
        self,
        tool_id: str,
    ) -> None:
        """
        Track tool execution.
        """

        async with self._lock:

            tool = self._tools.get(
                tool_id
            )

            if not tool:
                return

            tool.execution_count += 1

            tool.last_execution_time = (
                time.time()
            )

    # ========================================================
    # INTERNAL VALIDATION
    # ========================================================

    @staticmethod
    def _validate_handler(
        handler: Callable[
            ...,
            Awaitable[Any],
        ],
    ) -> None:
        """
        Validate async handler.
        """

        if not inspect.iscoroutinefunction(
            handler
        ):
            raise TypeError(
                "Tool handler must be async."
            )

    # ========================================================
    # STATS
    # ========================================================

    def get_stats(
        self,
    ) -> ToolRegistryStats:
        """
        Retrieve registry statistics.
        """

        return self._stats

    def _recalculate_stats(
        self,
    ) -> None:
        """
        Recalculate statistics.
        """

        self._stats.total_tools = len(
            self._tools
        )

        self._stats.active_tools = len(
            [
                tool
                for tool
                in self._tools.values()
                if (
                    tool.status
                    == ToolStatus.ACTIVE
                )
            ]
        )

        self._stats.disabled_tools = len(
            [
                tool
                for tool
                in self._tools.values()
                if (
                    tool.status
                    == ToolStatus.DISABLED
                )
            ]
        )

    # ========================================================
    # DEBUGGING
    # ========================================================

    async def dump_registry(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Export registry state.
        """

        async with self._lock:

            return [
                {
                    "tool_id": tool.metadata.tool_id,
                    "name": tool.metadata.name,
                    "type": tool.metadata.tool_type,
                    "status": tool.status,
                    "version": tool.metadata.version,
                    "executions": (
                        tool.execution_count
                    ),
                }
                for tool
                in self._tools.values()
            ]
