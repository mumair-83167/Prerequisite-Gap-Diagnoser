from typing import List, Optional, Set, Tuple
from collections import deque
from app.graph.loader import graph_store
from app.models.schemas import ConceptNode


class BackwardBFSTraversal:
    """
    Implements bounded backward Breadth-First Search over the concept graph's prerequisite edges.
    Enforces the depth <= 3 constraint (Rule §4).
    """

    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth

    def get_candidate_sequence(
        self,
        target_node_id: str,
        mastered_nodes: Optional[List[str]] = None,
    ) -> List[Tuple[ConceptNode, int]]:
        """
        Returns an ordered list of (ConceptNode, depth) tuples representing the
        nearest-first backward traversal order starting from target_node_id.
        """
        mastered_set: Set[str] = set(mastered_nodes or [])
        candidates: List[Tuple[ConceptNode, int]] = []
        visited: Set[str] = {target_node_id}

        # Queue contains (node_id, current_depth)
        queue: deque[Tuple[str, int]] = deque([(target_node_id, 0)])

        while queue:
            curr_id, curr_depth = queue.popleft()

            if curr_depth >= self.max_depth:
                continue

            # Look up prerequisites of curr_id
            curr_node = graph_store.get_node(curr_id)
            if not curr_node:
                continue

            for prereq_id in curr_node.prerequisites:
                if prereq_id not in visited:
                    visited.add(prereq_id)
                    prereq_node = graph_store.get_node(prereq_id)
                    if prereq_node:
                        # Only add to candidates if not already mastered
                        if prereq_id not in mastered_set:
                            candidates.append((prereq_node, curr_depth + 1))
                        # Still traverse into its prerequisites even if mastered,
                        # but stop at max_depth
                        queue.append((prereq_id, curr_depth + 1))

        return candidates

    def get_next_candidate(
        self,
        target_node_id: str,
        visited_in_session: List[str],
        mastered_nodes: Optional[List[str]] = None,
    ) -> Optional[ConceptNode]:
        """
        Returns the next unvisited candidate node to probe in the diagnostic loop.
        Returns None if all candidates within max_depth have been evaluated.
        """
        visited_set = set(visited_in_session)
        candidates = self.get_candidate_sequence(target_node_id, mastered_nodes)

        for node, depth in candidates:
            if node.id not in visited_set:
                return node

        return None


# Global traversal instance
traversal_engine = BackwardBFSTraversal(max_depth=3)
