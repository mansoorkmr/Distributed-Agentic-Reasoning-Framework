"""
Distributed Agentic Reasoning Framework (DARF)

Dependency Graph
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from dataclasses import field

from typing import Dict
from typing import Set


@dataclass(slots=True)
class DependencyGraph:

    graph: Dict[str, Set[str]] = field(
        default_factory=dict
    )

    metadata: dict = field(
        default_factory=dict
    )

    version: str = "1.0"

    # ---------------------------------------------------------
    # Graph Operations
    # ---------------------------------------------------------

    def add_node(
        self,
        node: str,
    ) -> None:

        self.graph.setdefault(
            node,
            set(),
        )

    def add_dependency(
        self,
        task: str,
        depends_on: str,
    ) -> None:

        self.add_node(task)

        self.add_node(depends_on)

        self.graph[task].add(
            depends_on,
        )

    def dependencies(
        self,
        task: str,
    ) -> list[str]:

        return sorted(

            self.graph.get(

                task,

                set(),

            )

        )

    def contains(
        self,
        task: str,
    ) -> bool:

        return task in self.graph

    def node_count(
        self,
    ) -> int:

        return len(self.graph)

    def clear(
        self,
    ) -> None:

        self.graph.clear()

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "nodes":

                {

                    k: sorted(v)

                    for k, v

                    in self.graph.items()

                },

            "node_count":

                self.node_count(),

            "metadata":

                self.metadata,

            "version":

                self.version,

        }

    def to_json(self):

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __str__(self):

        return (

            f"DependencyGraph({self.node_count()} nodes)"

        )

    def __repr__(self):

        return (

            f"<DependencyGraph nodes={self.node_count()}>"

        )