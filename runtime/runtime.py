"""
Distributed Agentic Reasoning Framework (DARF) - Runtime

Central orchestration layer coordinating all subsystems.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

# Export explicitly to prevent namespace pollution
__all__ = ["Runtime"]

logger = logging.getLogger(__name__)


class Runtime:
    """
    Main DARF runtime orchestrator.
    
    Coordinates the planner, execution engine, memory manager,
    agent registry, and message bus.
    """

    def __init__(self, config: Optional[Any] = None) -> None:
        """Initializes the DARF Runtime and its core subsystems."""
        
        # --------------------------------------------------
        # Deferred Imports (Protects against Circular Imports)
        # --------------------------------------------------
        from planner.planner import Planner
        from execution.execution_engine import ExecutionEngine
        from memory.manager.memory_manager import MemoryManager
        from agents.agent_registry import AgentRegistry
        from communication.message_bus import MessageBus
        
        from runtime.runtime_state import RuntimeState
        from runtime.runtime_config import RuntimeConfig
        from runtime.runtime_context import RuntimeContext
        from runtime.runtime_metrics import RuntimeMetrics
        from runtime.runtime_registry import RuntimeRegistry

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
        logger.info("DARF Runtime initialized.")

    def start(self) -> None:
        """Starts the runtime. Initializes automatically if not already ready."""
        if not self.state.is_ready():
            self.initialize()
        
        self.state.run()
        logger.info("DARF Runtime started.")

    def stop(self) -> None:
        """Stops the runtime and records shutdown metrics."""
        self.state.stop()
        self.metrics.record_shutdown()
        logger.info("DARF Runtime stopped.")

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
            from runtime.exceptions import RuntimeNotReadyError
            raise RuntimeNotReadyError("Runtime has not been initialized.")

    # ------------------------------------------------------
    # Execution
    # ------------------------------------------------------

    def plan(self, request: str) -> Any:
        """Generates an execution plan based on the request."""
        self.require_ready()
        self.metrics.record_request()
        
        result = self.planner.plan(request)
        return result

    def execute(self, execution_plan: Any, callables: Optional[Dict[str, Any]] = None) -> Any:
        """Executes a previously generated execution plan."""
        self.require_ready()
        
        if callables is None:
            callables = {}

        return self.execution_engine.execute(
            execution_plan,
            callables=callables,
        )

    def run(self, request: str, callables: Optional[Dict[str, Any]] = None) -> Any:
        """End-to-end operation: plans the request and executes it."""
        self.require_ready()

        try:
            plan_result = self.plan(request)
            execution_results = self.execute(
                plan_result.execution_plan, 
                callables
            )

            self.memory_manager.remember_episode(
                key=request,
                value="completed",
            )
            return execution_results

        except Exception as e:
            self.metrics.record_failure()
            logger.error(f"Runtime execution failed: {e}")
            raise

    # ------------------------------------------------------
    # Memory
    # ------------------------------------------------------

    def remember(self, key: str, value: Any) -> None:
        """Stores a key-value pair in the memory manager."""
        self.memory_manager.remember(key, value)

    def recall(self, key: str) -> Any:
        """Retrieves a value from the memory manager by key."""
        return self.memory_manager.recall(key)

    # ------------------------------------------------------
    # Communication
    # ------------------------------------------------------

    def publish(self, message: Any) -> Any:
        """Publishes a message to the message bus."""
        return self.message_bus.publish(message)

    def receive(self) -> Any:
        """Receives a message from the message bus."""
        return self.message_bus.receive()

    # ------------------------------------------------------
    # Agents
    # ------------------------------------------------------

    def register_agent(self, agent: Any) -> None:
        """Registers an agent with the agent registry."""
        self.agent_registry.register(agent)

    def unregister_agent(self, agent_id: str) -> None:
        """Unregisters an agent from the agent registry using its ID."""
        self.agent_registry.unregister(agent_id)

    def get_agent(self, agent_id: str) -> Any:
        """Retrieves an agent from the registry by its ID."""
        return self.agent_registry.get(agent_id)

    # ------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------

    def clear(self) -> None:
        """Clears runtime state without destroying components."""
        self.context.clear()
        self.registry.clear()
        self.memory_manager.clear()
        self.metrics.reset()
        logger.info("Runtime state cleared.")

    def reset(self) -> None:
        """Resets the runtime to its initial state."""
        self.stop()
        
        from runtime.runtime_state import RuntimeState
        from runtime.runtime_context import RuntimeContext
        from runtime.runtime_registry import RuntimeRegistry
        
        self.state = RuntimeState()
        self.context = RuntimeContext()
        self.metrics.reset()
        self.registry = RuntimeRegistry()

        # Re-register core components using the built-in helper methods
        self._register_components()
        self._build_context()
        logger.info("Runtime successfully reset.")

    # ------------------------------------------------------
    # Serialization
    # ------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the core runtime components to a dictionary."""
        return {
            "state": self.state.to_dict(),
            "config": self.config.to_dict(),
            "context": self.context.to_dict(),
            "metrics": self.metrics.to_dict(),
            "registry": self.registry.to_dict(),
            "version": "1.0",
        }

    def to_json(self) -> str:
        """Serializes the core runtime components to a JSON string."""
        return json.dumps(
            self.to_dict(),
            indent=4,
            sort_keys=True,
        )

    # ------------------------------------------------------
    # Representation
    # ------------------------------------------------------

    def __str__(self) -> str:
        return f"Runtime({self.state.status.value})"

    def __repr__(self) -> str:
        return (
            f"<Runtime "
            f"state='{self.state.status.value}' "
            f"components={self.registry.count()}>"
        )