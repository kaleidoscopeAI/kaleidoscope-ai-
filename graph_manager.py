perspective_engine/knowledge/graph_manager.py
Python

import networkx as nx

class GraphManager:
    def __init__(self):
        self.knowledge_graph = nx.DiGraph()

    def add_node(self, node_id: str, node_type: str, attributes: dict = None):
        """Add a node to the knowledge graph."""
        if attributes is None:
            attributes = {}
        self.knowledge_graph.add_node(node_id, type=node_type, **attributes)

    def add_edge(self, source_node: str, target_node: str, relationship: str, attributes: dict = None):
        """Add an edge between two nodes in the knowledge graph."""
        if attributes is None:
            attributes = {}
        self.knowledge_graph.add_edge(source_node, target_node, relationship=relationship, **attributes)

    def update_node_attributes(self, node_id: str, attributes: dict):
        """Update attributes of a node."""
        if node_id in self.knowledge_graph:
            self.knowledge_graph.nodes[node_id].update(attributes)

    def update_edge_attributes(self, source_node: str, target_node: str, attributes: dict):
        """Update attributes of an edge."""
        if self.knowledge_graph.has_edge(source_node, target_node):
            self.knowledge_graph[source_node][target_node].update(attributes)

    def get_node_attributes(self, node_id: str) -> dict:
        """Get attributes of a node."""
        if node_id in self.knowledge_graph:
            return self.knowledge_graph.nodes[node_id]
        return {}

    def get_edge_attributes(self, source_node: str, target_node: str) -> dict:
        """Get attributes of an edge."""
        if self.knowledge_graph.has_edge(source_node, target_node):
            return self.knowledge_graph[source_node][target_node]
        return {}

    def find_nodes(self, node_type: str = None, attribute_filter: dict = None) -> list:
        """Find nodes based on type and/or attribute filter."""
        nodes = []
        for node_id, attributes in self.knowledge_graph.nodes(data=True):
            if node_type is None or attributes.get('type') == node_type:
                if attribute_filter is None or all(attributes.get(key) == value for key, value in attribute_filter.items()):
                    nodes.append(node_id)
        return nodes

    def find_edges(self, relationship: str = None, attribute_filter: dict = None) -> list:
        """Find edges based on relationship and/or attribute filter."""
        edges = []
        for source, target, attributes in self.knowledge_graph.edges(data=True):
            if relationship is None or attributes.get('relationship') == relationship:
                if attribute_filter is None or all(
                if attribute_filter is None or all(attributes.get(key) == value for key, value in attribute_filter.items()):
                    edges.append((source, target))
        return edges

    def get_neighbors(self, node_id: str, relationship: str = None) -> list:
        """Get neighbors of a node, optionally filtered by relationship."""
        neighbors = []
        if node_id in self.knowledge_graph:
            for neighbor in self.knowledge_graph.neighbors(node_id):
                if relationship is None or self.knowledge_graph[node_id][neighbor].get('relationship') == relationship:
                    neighbors.append(neighbor)
        return neighbors

    def shortest_path(self, source_node: str, target_node: str) -> list:
        """Find the shortest path between two nodes."""
        try:
            return nx.shortest_path(self.knowledge_graph, source_node, target_node)
        except nx.NetworkXNoPath:
            return []

    def visualize_graph(self):
        """Visualize the knowledge graph (basic implementation)."""
        nx.draw(self.knowledge_graph, with_labels=True)
        
    def get_subgraph(self, node_ids: List[str]) -> nx.DiGraph:
        """
        Extract a subgraph based on a list of node IDs.
        """
        return self.knowledge_graph.subgraph(node_ids)

    def calculate_centrality(self, centrality_type: str = 'degree') -> dict:
        """
        Calculate centrality measures for the nodes in the graph.
        Supported centrality types: 'degree', 'betweenness', 'closeness', 'eigenvector'.
        """
        if centrality_type == 'degree':
            centrality = nx.degree_centrality(self.knowledge_graph)
        elif centrality_type == 'betweenness':
            centrality = nx.betweenness_centrality(self.knowledge_graph)
        elif centrality_type == 'closeness':
            centrality = nx.closeness_centrality(self.knowledge_graph)
        elif centrality_type == 'eigenvector':
            centrality = nx.eigenvector_centrality(self.knowledge_graph)
        else:
            raise ValueError(f"Centrality type '{centrality_type}' not supported.")
        return centrality
    
    def get_state(self) -> dict:
      """Return the current state of the graph manager."""
      return {
          'nodes': [{node_id: data} for node_id, data in self.knowledge_graph.nodes(data=True)],
          'edges': [{source: {target: data}} for source, target, data in self.knowledge_graph.edges(data=True)]
      }
