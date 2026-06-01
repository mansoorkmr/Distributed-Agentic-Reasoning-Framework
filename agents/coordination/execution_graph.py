"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Execution Graph Infrastructure

Author:
    DARF Coordination Systems Division

Purpose:
    Enterprise-grade execution graph orchestration
    infrastructure for:

        - distributed multi-agent systems
        - institutional execution orchestration
        - workflow dependency management
        - scalable execution planning
        - HPC-aware execution coordination
        - distributed reasoning pipelines
        - execution DAG management
        - production-grade workflow systems

Core Responsibilities:
    - execution graph orchestration
    - dependency management
    - workflow DAG construction
    - execution stage scheduling
    - distributed-safe coordination
    - graph validation
    - execution topology management
    - institutional observability

Design Principles:
    - deterministic
    - distributed-safe
    - scalable
    - fault-tolerant
    - institutionally reproducible
    - production-grade
    - dependency-aware
    - future extensible

Supported Features:
    - DAG-based execution planning
    - dependency validation
    - parallel execution analysis
    - topological execution ordering
    - workflow synchronization
    - execution tracing
    - telemetry-aware orchestration
    - institutional graph infrastructure
"""

import json
import traceback
import uuid
from collections import defaultdict
from collections import deque
from datetime import datetime
from typing import Any
from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from infrastructure.logging.structured_logger import (
    get_logger,
)

from agents.runtime.runtime_context import (
    RuntimeContext,
)


class ExecutionGraph:
    """
    Institutional-grade execution graph.

    Handles:
        - workflow DAG orchestration
        - dependency resolution
        - execution ordering
        - distributed-safe coordination
        - graph validation
    """

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(
        self,
        enable_parallel_execution: bool = True,
        enable_dependency_validation: bool = True,
        telemetry_enabled: bool = True,
    ):

        self.enable_parallel_execution = (
            enable_parallel_execution
        )

        self.enable_dependency_validation = (
            enable_dependency_validation
        )

        self.telemetry_enabled = (
            telemetry_enabled
        )

        self.logger = get_logger(

            name="ExecutionGraph",

            log_dir="logs/agents",
        )

        # ========================================================
        # GRAPH STORAGE
        # ========================================================

        self.graph_id = str(uuid.uuid4())

        self.nodes: Dict[
            str,
            Dict[str, Any]
        ] = {}

        self.edges: List[
            Dict[str, str]
        ] = []

        self.adjacency_list: DefaultDict[
            str,
            List[str]
        ] = defaultdict(list)

        self.reverse_dependencies: DefaultDict[
            str,
            List[str]
        ] = defaultdict(list)

        # ========================================================
        # TELEMETRY
        # ========================================================

        self.total_nodes = 0

        self.total_edges = 0

        self.created_at = (
            datetime.utcnow().isoformat()
        )

        self.logger.info(
            "ExecutionGraph initialized successfully."
        )

    # ============================================================
    # ADD NODE
    # ============================================================

    def add_node(
        self,
        node: Dict[str, Any],
    ):
        """
        Add execution node safely.
        """

        required_fields = [

            "task",

            "agent",
        ]

        for field in required_fields:

            if field not in node:

                raise ValueError(
                    f"Missing required "
                    f"field: {field}"
                )

        task_name = node["task"]

        if task_name in self.nodes:

            raise ValueError(
                f"Duplicate node detected: "
                f"{task_name}"
            )

        self.nodes[
            task_name
        ] = node

        self.total_nodes += 1

        self.logger.info(
            f"Execution node added | "
            f"Task={task_name}"
        )

    # ============================================================
    # ADD EDGE
    # ============================================================

    def add_edge(
        self,
        source: str,
        target: str,
    ):
        """
        Add execution dependency safely.
        """

        if source not in self.nodes:

            raise ValueError(
                f"Source node missing: "
                f"{source}"
            )

        if target not in self.nodes:

            raise ValueError(
                f"Target node missing: "
                f"{target}"
            )

        edge = {

            "source":
                source,

            "target":
                target,
        }

        if edge not in self.edges:

            self.edges.append(edge)

            self.adjacency_list[
                source
            ].append(target)

            self.reverse_dependencies[
                target
            ].append(source)

            self.total_edges += 1

            self.logger.info(
                f"Execution edge added | "
                f"{source} -> {target}"
            )

    # ============================================================
    # BUILD GRAPH
    # ============================================================

    def build_graph(
        self,
        subtasks: List[
            Dict[str, Any]
        ],
        context: Optional[
            RuntimeContext
        ] = None,
    ) -> Dict[str, Any]:
        """
        Institutional-grade graph construction.
        """

        try:

            if context is None:

                context = RuntimeContext(

                    user_query="graph_execution"
                )

            context.execution_state = (
                "graph_building"
            )

            # ----------------------------------------------------
            # NODE CONSTRUCTION
            # ----------------------------------------------------

            for subtask in subtasks:

                self.add_node(subtask)

            # ----------------------------------------------------
            # DEPENDENCY CONSTRUCTION
            # ----------------------------------------------------

            for subtask in subtasks:

                task_name = subtask[
                    "task"
                ]

                dependencies = subtask.get(

                    "dependencies",

                    [],
                )

                for dependency in dependencies:

                    self.add_edge(

                        dependency,

                        task_name,
                    )

            # ----------------------------------------------------
            # VALIDATION
            # ----------------------------------------------------

            validation_result = (
                self.validate_graph()
            )

            # ----------------------------------------------------
            # EXECUTION STAGES
            # ----------------------------------------------------

            execution_stages = (
                self.compute_execution_stages()
            )

            result = {

                "graph_id":
                    self.graph_id,

                "nodes":
                    self.nodes,

                "edges":
                    self.edges,

                "execution_stages":
                    execution_stages,

                "validation":
                    validation_result,

                "parallel_execution":
                    self.enable_parallel_execution,

                "success":
                    True,
            }

            self.logger.info(
                f"Execution graph built | "
                f"Nodes={self.total_nodes} | "
                f"Edges={self.total_edges}"
            )

            return result

        except Exception as error:

            self.logger.error(
                f"Execution graph build failed | "
                f"Error={error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

            return {

                "success":
                    False,

                "error":
                    str(error),
            }

    # ============================================================
    # VALIDATE DAG
    # ============================================================

    def validate_graph(
        self,
    ) -> Dict[str, Any]:
        """
        Validate graph integrity safely.
        """

        validation = {

            "valid":
                True,

            "issues":
                [],

            "is_dag":
                True,
        }

        if len(self.nodes) == 0:

            validation[
                "valid"
            ] = False

            validation[
                "issues"
            ].append(
                "No graph nodes detected."
            )

        if self.detect_cycle():

            validation[
                "valid"
            ] = False

            validation[
                "is_dag"
            ] = False

            validation[
                "issues"
            ].append(
                "Cycle detected in execution graph."
            )

        return validation

    # ============================================================
    # DETECT CYCLE
    # ============================================================

    def detect_cycle(
        self,
    ) -> bool:
        """
        Detect cycles using DFS safely.
        """

        visited: Set[str] = set()

        recursion_stack: Set[str] = set()

        def dfs(
            node: str,
        ) -> bool:

            visited.add(node)

            recursion_stack.add(node)

            for neighbor in self.adjacency_list[
                node
            ]:

                if neighbor not in visited:

                    if dfs(neighbor):

                        return True

                elif neighbor in recursion_stack:

                    return True

            recursion_stack.remove(node)

            return False

        for node in self.nodes:

            if node not in visited:

                if dfs(node):

                    return True

        return False

    # ============================================================
    # TOPOLOGICAL SORT
    # ============================================================

    def topological_sort(
        self,
    ) -> List[str]:
        """
        Perform DAG-safe topological ordering.
        """

        in_degree = {

            node: 0

            for node in self.nodes
        }

        for edge in self.edges:

            target = edge["target"]

            in_degree[target] += 1

        queue = deque([

            node

            for node, degree
            in in_degree.items()

            if degree == 0
        ])

        ordered_nodes = []

        while queue:

            current = queue.popleft()

            ordered_nodes.append(current)

            for neighbor in self.adjacency_list[
                current
            ]:

                in_degree[
                    neighbor
                ] -= 1

                if in_degree[
                    neighbor
                ] == 0:

                    queue.append(neighbor)

        if len(
            ordered_nodes
        ) != len(self.nodes):

            raise RuntimeError(
                "Topological sort failed."
            )

        return ordered_nodes

    # ============================================================
    # COMPUTE EXECUTION STAGES
    # ============================================================

    def compute_execution_stages(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Compute execution stages safely.
        """

        ordered_nodes = (
            self.topological_sort()
        )

        stages = []

        processed = set()

        current_stage_index = 1

        while len(processed) < len(
            ordered_nodes
        ):

            stage_tasks = []

            for node in ordered_nodes:

                if node in processed:

                    continue

                dependencies = set(

                    self.reverse_dependencies[
                        node
                    ]
                )

                if dependencies.issubset(
                    processed
                ):

                    stage_tasks.append(node)

            if not stage_tasks:

                break

            stages.append(

                {

                    "stage":
                        current_stage_index,

                    "tasks":
                        stage_tasks,

                    "parallelizable":
                        len(stage_tasks) > 1,
                }
            )

            processed.update(stage_tasks)

            current_stage_index += 1

        return stages

    # ============================================================
    # GET ROOT NODES
    # ============================================================

    def get_root_nodes(
        self,
    ) -> List[str]:
        """
        Return execution roots safely.
        """

        roots = []

        for node in self.nodes:

            if len(

                self.reverse_dependencies[
                    node
                ]

            ) == 0:

                roots.append(node)

        return roots

    # ============================================================
    # GET LEAF NODES
    # ============================================================

    def get_leaf_nodes(
        self,
    ) -> List[str]:
        """
        Return execution leaves safely.
        """

        leaves = []

        for node in self.nodes:

            if len(

                self.adjacency_list[
                    node
                ]

            ) == 0:

                leaves.append(node)

        return leaves

    # ============================================================
    # TELEMETRY
    # ============================================================

    def telemetry(
        self,
    ) -> Dict[str, Any]:
        """
        Return institutional telemetry safely.
        """

        return {

            "graph_id":
                self.graph_id,

            "total_nodes":
                self.total_nodes,

            "total_edges":
                self.total_edges,

            "parallel_execution":
                self.enable_parallel_execution,

            "dependency_validation":
                self.enable_dependency_validation,

            "root_nodes":
                len(
                    self.get_root_nodes()
                ),

            "leaf_nodes":
                len(
                    self.get_leaf_nodes()
                ),

            "created_at":
                self.created_at,
        }

    # ============================================================
    # EXPORT GRAPH
    # ============================================================

    def export_graph(
        self,
        output_path: str,
    ):
        """
        Export execution graph safely.
        """

        exported = {

            "graph_id":
                self.graph_id,

            "nodes":
                self.nodes,

            "edges":
                self.edges,

            "execution_stages":
                self.compute_execution_stages(),

            "telemetry":
                self.telemetry(),
        }

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(

                exported,

                file,

                indent=4,

                ensure_ascii=False,
            )

        self.logger.info(
            f"Execution graph exported | "
            f"Path={output_path}"
        )

    # ============================================================
    # RESET GRAPH
    # ============================================================

    def reset(
        self,
    ):
        """
        Reset execution graph safely.
        """

        self.nodes.clear()

        self.edges.clear()

        self.adjacency_list.clear()

        self.reverse_dependencies.clear()

        self.total_nodes = 0

        self.total_edges = 0

        self.graph_id = str(
            uuid.uuid4()
        )

        self.logger.warning(
            "Execution graph reset."
        )

    # ============================================================
    # SUMMARY
    # ============================================================

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return institutional graph summary.
        """

        return {

            "graph_id":
                self.graph_id,

            "nodes":
                self.total_nodes,

            "edges":
                self.total_edges,

            "parallel_execution":
                self.enable_parallel_execution,

            "is_dag":
                not self.detect_cycle(),

            "created_at":
                self.created_at,
        }

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(
        self,
    ):

        return (

            f"ExecutionGraph("
            f"nodes={self.total_nodes}, "
            f"edges={self.total_edges})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    execution_graph = ExecutionGraph(

        enable_parallel_execution=True,

        enable_dependency_validation=True,
    )

    subtasks = [

        {

            "task":
                "semantic_analysis",

            "agent":
                "planner_agent",

            "dependencies":
                [],
        },

        {

            "task":
                "knowledge_retrieval",

            "agent":
                "retrieval_agent",

            "dependencies":
                ["semantic_analysis"],
        },

        {

            "task":
                "domain_reasoning",

            "agent":
                "reasoning_agent",

            "dependencies":
                ["semantic_analysis"],
        },

        {

            "task":
                "response_aggregation",

            "agent":
                "aggregator_agent",

            "dependencies": [

                "knowledge_retrieval",

                "domain_reasoning",
            ],
        },
    ]

    context = RuntimeContext(

        user_query=(
            "Build institutional "
            "AI workflow graph."
        )
    )

    result = execution_graph.build_graph(

        subtasks=subtasks,

        context=context,
    )

    print("\nExecution Graph Result:\n")

    print(
        json.dumps(
            result,
            indent=4,
        )
    )

    print("\nExecution Graph Telemetry:\n")

    print(
        json.dumps(
            execution_graph.telemetry(),
            indent=4,
        )
    )
