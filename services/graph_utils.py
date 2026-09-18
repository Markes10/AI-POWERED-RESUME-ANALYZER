"""
Graph utilities for Learning Path Recommender.

- Build a skill–course knowledge graph
- Run simple graph queries
"""

from typing import List, Dict, Any
import networkx as nx


# -------------------------------
# Graph Manager
# -------------------------------
class LearningGraph:
    """
    Wrapper around a NetworkX directed graph for skills ↔ courses.
    """

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_skill(self, skill: str):
        self.graph.add_node(skill, type="skill")

    def add_course(self, course: str):
        self.graph.add_node(course, type="course")

    def link_skill_to_course(self, skill: str, course: str):
        self.add_skill(skill)
        self.add_course(course)
        self.graph.add_edge(skill, course)

    def link_course_to_skill(self, course: str, skill: str):
        self.add_course(course)
        self.add_skill(skill)
        self.graph.add_edge(course, skill)

    def query_related(self, node: str, depth: int = 1) -> Dict[str, Any]:
        """
        Query related nodes up to a given depth.
        """
        if node not in self.graph:
            return {"error": f"Node '{node}' not found in graph."}

        neighbors = nx.single_source_shortest_path_length(self.graph, node, cutoff=depth)
        related_nodes = list(neighbors.keys())
        related_nodes.remove(node)

        edges = []
        for n in related_nodes:
            if self.graph.has_edge(node, n):
                edges.append({"from": node, "to": n})
            if self.graph.has_edge(n, node):
                edges.append({"from": n, "to": node})

        return {
            "node": node,
            "related_nodes": related_nodes,
            "edges": edges
        }

    def export_graph(self) -> Dict[str, Any]:
        """
        Export nodes and edges for visualization in frontend (e.g., D3.js).
        """
        nodes = [{"id": n, "type": self.graph.nodes[n].get("type", "unknown")} for n in self.graph.nodes]
        edges = [{"from": u, "to": v} for u, v in self.graph.edges]

        return {"nodes": nodes, "edges": edges}


# -------------------------------
# Singleton
# -------------------------------
_graph_instance: LearningGraph = None


def get_graph() -> LearningGraph:
    """
    Get a singleton LearningGraph instance.
    """
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = LearningGraph()
        _seed_graph(_graph_instance)
    return _graph_instance


# -------------------------------
# Seed with Example Data
# -------------------------------
def _seed_graph(graph: LearningGraph):
    """
    Populate the graph with sample skills and courses.
    Later: replace with DB ingestion.
    """
    graph.link_skill_to_course("Python", "Python for Data Science")
    graph.link_skill_to_course("SQL", "Advanced SQL")
    graph.link_skill_to_course("Data Analysis", "Machine Learning Basics")
    graph.link_course_to_skill("Machine Learning Basics", "Machine Learning")
