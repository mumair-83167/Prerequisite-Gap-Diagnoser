import pytest
from app.engine.traversal import BackwardBFSTraversal
from app.graph.loader import graph_store


def test_candidate_sequence_from_recursion():
    """Verify BFS traversal from 'recursion' produces candidates within depth <= 3."""
    traversal = BackwardBFSTraversal(max_depth=3)
    candidates = traversal.get_candidate_sequence("recursion")

    assert len(candidates) > 0
    node_ids = [n.id for n, depth in candidates]
    depths = [depth for n, depth in candidates]

    # Check depth constraints
    assert all(1 <= d <= 3 for d in depths)

    # Nearest-first ordering: depths should be monotonically non-decreasing
    for i in range(len(depths) - 1):
        assert depths[i] <= depths[i + 1]

    # Level 1 nodes must include base_case and call_stack
    assert "base_case" in node_ids
    assert "call_stack" in node_ids
    assert "recursive_step" in node_ids

    # Conditionals is a prerequisite of base_case, so it must appear at depth <= 3
    assert "conditionals" in node_ids


def test_skip_mastered_nodes():
    """Verify already mastered nodes are excluded from candidate list."""
    traversal = BackwardBFSTraversal(max_depth=3)
    # Mark base_case as mastered
    candidates = traversal.get_candidate_sequence("recursion", mastered_nodes=["base_case"])
    node_ids = [n.id for n, depth in candidates]

    assert "base_case" not in node_ids
    # But prerequisites of base_case (conditionals) should still be reachable
    assert "conditionals" in node_ids


def test_get_next_candidate_progressive():
    """Verify get_next_candidate steps through candidates sequentially."""
    traversal = BackwardBFSTraversal(max_depth=3)
    visited = []

    first = traversal.get_next_candidate("recursion", visited)
    assert first is not None
    visited.append(first.id)

    second = traversal.get_next_candidate("recursion", visited)
    assert second is not None
    assert second.id != first.id
    visited.append(second.id)

    third = traversal.get_next_candidate("recursion", visited)
    assert third is not None
    assert third.id not in [first.id, second.id]


def test_exhaustion_returns_none():
    """Verify returns None when all candidates within max_depth have been visited."""
    traversal = BackwardBFSTraversal(max_depth=1)
    all_level_1 = [n.id for n, d in traversal.get_candidate_sequence("recursion")]

    # If all visited, next is None
    next_node = traversal.get_next_candidate("recursion", visited_in_session=all_level_1)
    assert next_node is None
