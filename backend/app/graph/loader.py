import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from app.models.schemas import ConceptGraph, ConceptNode


class GraphIntegrityError(ValueError):
    """Raised when the concept graph violates topological or referential invariants."""
    pass


class ConceptGraphStore:
    """
    Singleton in-memory store for the frozen concept graph.
    Loads, validates, and indexes nodes at startup.
    """

    def __init__(self, json_path: Optional[Path] = None):
        self._json_path = json_path or (Path(__file__).parent / "concept_graph.json")
        self._graph: Optional[ConceptGraph] = None
        self._nodes_by_id: Dict[str, ConceptNode] = {}

    def load(self, force_reload: bool = False) -> ConceptGraph:
        if self._graph is not None and not force_reload:
            return self._graph

        if not self._json_path.exists():
            raise FileNotFoundError(f"Concept graph JSON not found at: {self._json_path}")

        with open(self._json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        graph = ConceptGraph(**raw_data)
        self.validate(graph)

        self._graph = graph
        self._nodes_by_id = {node.id: node for node in graph.nodes}
        return self._graph

    def get_graph(self) -> ConceptGraph:
        if self._graph is None:
            return self.load()
        return self._graph

    def get_node(self, node_id: str) -> Optional[ConceptNode]:
        if self._graph is None:
            self.load()
        return self._nodes_by_id.get(node_id)

    def get_prerequisites(self, node_id: str) -> List[ConceptNode]:
        node = self.get_node(node_id)
        if not node:
            return []
        return [self._nodes_by_id[prereq_id] for prereq_id in node.prerequisites if prereq_id in self._nodes_by_id]

    @staticmethod
    def validate(graph: ConceptGraph) -> None:
        """
        Validates fundamental graph invariants:
        1. Unique node IDs
        2. Referential integrity: all prerequisite IDs exist
        3. Acyclicity: no circular prerequisite dependencies (strict DAG)
        4. Target demo node exists
        """
        # 1. Uniqueness
        node_ids = set()
        for node in graph.nodes:
            if node.id in node_ids:
                raise GraphIntegrityError(f"Duplicate node ID detected: '{node.id}'")
            node_ids.add(node.id)

        # 2. Referential integrity
        for node in graph.nodes:
            for prereq_id in node.prerequisites:
                if prereq_id not in node_ids:
                    raise GraphIntegrityError(
                        f"Node '{node.id}' references non-existent prerequisite '{prereq_id}'"
                    )

        # 3. Acyclicity via DFS cycle detection
        # adjacency: node -> prerequisites (edges point from dependent to prerequisite)
        adj: Dict[str, List[str]] = {node.id: node.prerequisites for node in graph.nodes}
        visited: Dict[str, int] = {node_id: 0 for node_id in node_ids}  # 0: unvisited, 1: visiting, 2: visited

        def dfs(current_id: str, path: List[str]):
            visited[current_id] = 1  # visiting
            path.append(current_id)

            for neighbor in adj.get(current_id, []):
                if visited[neighbor] == 1:
                    cycle = " -> ".join(path + [neighbor])
                    raise GraphIntegrityError(f"Cycle detected in concept graph: {cycle}")
                if visited[neighbor] == 0:
                    dfs(neighbor, path)

            path.pop()
            visited[current_id] = 2  # visited

        for node_id in node_ids:
            if visited[node_id] == 0:
                dfs(node_id, [])

        # 4. Target demo node check
        if graph.target_node_id and graph.target_node_id not in node_ids:
            raise GraphIntegrityError(
                f"Target node ID '{graph.target_node_id}' does not exist in graph"
            )

        # 5. Demo path check
        for step in graph.demo_path:
            if step not in node_ids:
                raise GraphIntegrityError(
                    f"Demo path step '{step}' does not exist in graph"
                )


# Global store instance
graph_store = ConceptGraphStore()


def get_concept_graph() -> ConceptGraph:
    """Convenience getter for the global concept graph."""
    return graph_store.get_graph()
