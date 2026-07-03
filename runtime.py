"""
Distributed Agentic Reasoning Framework (DARF) - Runtime

Central orchestration layer coordinating all subsystems.
"""

from __future__ import annotations

from typing import Any, Optional

# Subsystem Imports
from planner.planner import Planner
from execution.execution_engine import ExecutionEngine
from memory.manager.memory_manager import MemoryManager
from agents.agent_registry import AgentRegistry
from communication.message_bus import MessageBus

# Runtime Imports
from runtime.runtime_state import RuntimeState
from runtime.runtime_config import RuntimeConfig
from runtime.runtime_context import RuntimeContext
from runtime.runtime_metrics import RuntimeMetrics
from runtime.runtime_registry import RuntimeRegistry
from runtime.exceptions import RuntimeNotReadyError

# Explicitly declare what is exported when someone uses 'import *'
__all__ = ["Runtime"]


class Runtime:
    """
    Main DARF runtime orchestrator.
    
    Coordinates the planner, execution engine, memory manager,
    agent registry, and message bus.
    """

    def __init__(self, config: Optional[RuntimeConfig] = None) -> None:
        """Initializes the DARF Runtime and its core subsystems."""
        self.config = config or RuntimeConfig()
        self.state = RuntimeState()
        self.context = RuntimeContext()
        self.metrics = RuntimeMetrics()
        self.registry = RuntimeRegistry()

        # --------------------------------------------------
        # Core subsystems
        # --------------------------------------------------
        self.planner = Planner()
        self.execution_engine = ExecutionEngine()
        self.memory_manager = MemoryManager()
        self.agent_registry = AgentRegistry()
        self.message_bus = MessageBus()

        # Initialize internal bindings
        self._register_components()
        self._build_context()

    def _register_components(self) -> None:
        """Registers all core subsystems into the runtime registry."""
        self.registry.register("planner", self.planner)
        self.registry.register("execution_engine", self.execution_engine)
        self.registry.register("memory_manager", self.memory_manager)
        self.registry.register("agent_registry", self.agent_registry)
        self.registry.register("message_bus", self.message_bus)

    def _build_context(self) -> None:
        """Attaches core subsystems to the runtime context."""
        self.context.planner = self.planner
        self.context.execution_engine = self.execution_engine
        self.context.memory_manager = self.memory_manager
        self.context.agent_registry = self.agent_registry
        self.context.message_bus = self.message_bus

    # ------------------------------------------------------
    # Lifecycle Management
    # ------------------------------------------------------

    def initialize(self) -> None:
        """Initializes runtime states and records startup metrics."""
        self.state.initialize()
        self.state.ready()
        self.metrics.record_startup()

    def start(self) -> None:
        """Starts the runtime. Initializes automatically if not already ready."""
        if not self.state.is_ready():
            self.initialize()
        
        self.state.run()

    def stop(self) -> None:
        """Stops the runtime and records shutdown metrics."""
        self.state.stop()
        self.metrics.record_shutdown()

    # ------------------------------------------------------
    # Health and Diagnostics
    # ------------------------------------------------------

    def is_ready(self) -> bool:
        """Returns True if the runtime is initialized and ready."""
        return self.state.is_ready()

    def is_running(self) -> bool:
        """Returns True if the runtime is currently executing."""
        return self.state.is_running()

    def component(self, name: str) -> Any:
        """Retrieves a registered component by its string name."""
        return self.registry.get(name)

    def require_ready(self) -> None:
        """
        Ensures the runtime is ready or running.
        
        Raises:
            RuntimeNotReadyError: If the runtime has not been initialized.
        """
        if not (self.state.is_ready() or self.state.is_running()):
            raise RuntimeNotReadyError("Runtime has not been initialized.")