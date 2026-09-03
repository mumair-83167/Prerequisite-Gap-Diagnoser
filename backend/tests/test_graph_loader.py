import pytest
from app.graph.loader import ConceptGraphStore, GraphIntegrityError, get_concept_graph
from app.models.schemas import ConceptGraph, ConceptNode


def test_graph_loads_successfully():
    """Verify concept_graph.json is loaded and parsed into ConceptGraph schema."""
    graph = get_concept_graph()
    assert isinstance(graph, ConceptGraph)
    assert graph.version == "1.0.0"
    assert graph.domain == "python_fundamentals"


def test_graph_node_count_and_target():
    """Verify node count is bounded between 20-25 per scope discipline rules."""
    graph = get_concept_graph()
    assert 20 <= len(graph.nodes) <= 25
    assert graph.target_node_id == "recursion"

    # Verify target node exists in nodes
    target = next((n for n in graph.nodes if n.id == "recursion"), None)
    assert target is not None
    assert target.tier == 5


def test_referential_integrity():
    """Verify all prerequisite references resolve to existing concept nodes."""
    graph = get_concept_graph()
    node_ids = {n.id for n in graph.nodes}

    for node in graph.nodes:
        for prereq in node.prerequisites:
            assert prereq in node_ids, f"Node '{node.id}' has unresolvable prerequisite '{prereq}'"


def test_dag_acyclicity():
    """Verify the graph is strictly acyclic (DAG)."""
    graph = get_concept_graph()
    # ConceptGraphStore.validate raises GraphIntegrityError if any cycle exists
    ConceptGraphStore.validate(graph)


def test_demo_path_completeness():
    """
    Verify every node on the demo path has high-quality, rich grounding metadata:
    - Non-empty description
    - Observable mastery signal
    - Micro-lesson (<20s read)
    - Teach-back rubric with >= 2 items
    - Sample problem with Pyodide test harness
    """
    graph = get_concept_graph()
    nodes_by_id = {n.id: n for n in graph.nodes}

    for node_id in graph.demo_path:
        node = nodes_by_id.get(node_id)
        assert node is not None, f"Demo path node '{node_id}' missing from graph"
        assert len(node.description.strip()) > 10
        assert len(node.mastery_signal.strip()) > 10
        assert len(node.micro_lesson.strip()) > 20
        assert len(node.teach_back_rubric) >= 2
        assert node.sample_problem is not None
        assert len(node.sample_problem.test_harness.strip()) > 5


def test_cycle_detection_catches_cycle():
    """Verify graph validator catches an artificial cycle and raises GraphIntegrityError."""
    cyclic_nodes = [
        ConceptNode(
            id="node_a",
            name="Node A",
            tier=0,
            prerequisites=["node_b"],
            description="Test A",
            mastery_signal="Signal A",
            micro_lesson="Lesson A",
            teach_back_rubric=["Point 1", "Point 2"],
        ),
        ConceptNode(
            id="node_b",
            name="Node B",
            tier=0,
            prerequisites=["node_a"],
            description="Test B",
            mastery_signal="Signal B",
            micro_lesson="Lesson B",
            teach_back_rubric=["Point 1", "Point 2"],
        ),
    ]
    cyclic_graph = ConceptGraph(version="1.0.0", target_node_id="node_a", nodes=cyclic_nodes)

    with pytest.raises(GraphIntegrityError, match="Cycle detected"):
        ConceptGraphStore.validate(cyclic_graph)


def test_missing_prerequisite_catches_broken_link():
    """Verify graph validator catches a missing prerequisite reference."""
    broken_nodes = [
        ConceptNode(
            id="node_x",
            name="Node X",
            tier=0,
            prerequisites=["non_existent_node"],
            description="Test X",
            mastery_signal="Signal X",
            micro_lesson="Lesson X",
            teach_back_rubric=["Point 1", "Point 2"],
        )
    ]
    broken_graph = ConceptGraph(version="1.0.0", target_node_id="node_x", nodes=broken_nodes)

    with pytest.raises(GraphIntegrityError, match="references non-existent prerequisite"):
        ConceptGraphStore.validate(broken_graph)
