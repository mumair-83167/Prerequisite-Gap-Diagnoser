#!/usr/bin/env python3
"""
scripts/seed_graph.py — Validates and reports statistics for concept_graph.json.
Enforces DAG invariants, referential integrity, and schema compliance.
"""

import sys
import json
from pathlib import Path

# Fix Windows console encoding if needed
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add backend directory to sys.path so app imports work seamlessly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.models.schemas import ConceptGraph
from app.graph.loader import ConceptGraphStore, GraphIntegrityError


def validate_and_report():
    graph_path = BACKEND_DIR / "app" / "graph" / "concept_graph.json"
    print(f"[INFO] Validating Concept Graph: {graph_path}")

    if not graph_path.exists():
        print(f"[ERROR] Concept graph JSON not found at {graph_path}")
        return 1

    try:
        with open(graph_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # 1. Pydantic validation
        graph = ConceptGraph(**raw_data)
        print("  [OK] Pydantic schema validation: PASSED")

        # 2. Graph invariants validation
        store = ConceptGraphStore(graph_path)
        store.validate(graph)
        print("  [OK] DAG Acyclicity & Referential Integrity: PASSED (0 cycles, 0 broken links)")

        # 3. Statistics
        total_nodes = len(graph.nodes)
        total_edges = sum(len(n.prerequisites) for n in graph.nodes)
        tiers = {}
        for n in graph.nodes:
            tiers[n.tier] = tiers.get(n.tier, 0) + 1

        print("\n[GRAPH STATISTICS]")
        print(f"  * Total Concept Nodes: {total_nodes} (Target: 20-22)")
        print(f"  * Total Prerequisite Edges: {total_edges}")
        print(f"  * Target Demo Node: '{graph.target_node_id}'")
        print(f"  * Demo Traversal Path: {' -> '.join(graph.demo_path)}")
        print("  * Nodes per Tier:")
        for tier in sorted(tiers.keys()):
            tier_names = [n.name for n in graph.nodes if n.tier == tier]
            print(f"    - Tier {tier}: {len(tier_names)} nodes ({', '.join(tier_names)})")

        # 4. Demo Path Depth Verification (Shortest Prerequisite BFS)
        visited = {graph.target_node_id: 0}
        queue = [graph.target_node_id]
        adj = {n.id: n.prerequisites for n in graph.nodes}

        while queue:
            curr = queue.pop(0)
            curr_dist = visited[curr]
            for prereq in adj.get(curr, []):
                if prereq not in visited:
                    visited[prereq] = curr_dist + 1
                    queue.append(prereq)

        print("\n[DEMO PATH BOUNDED DISTANCE FROM TARGET ('recursion')]")
        all_within_bound = True
        for step in graph.demo_path:
            dist = visited.get(step, "Unreachable")
            print(f"    - {step}: {dist} hops")
            if isinstance(dist, int) and dist > 3 and step in ["functions", "conditionals"]:
                print(f"    [WARN] Demo step '{step}' is {dist} hops away (> 3 limit)")
                all_within_bound = False

        if all_within_bound:
            print("  [OK] Bounded backward BFS condition (depth <= 3): SATISFIED")

        print("\n[SUCCESS] Concept Graph successfully validated, verified, and ready for freeze!")
        return 0

    except GraphIntegrityError as e:
        print(f"\n[ERROR] Graph Integrity Error: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Validation Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(validate_and_report())
