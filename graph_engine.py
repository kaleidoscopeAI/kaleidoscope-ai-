erspective_engine/core/graph_engine.py
Python

import networkx as nx
import numpy as np

class GraphEngine:
    def __init__(self, resonance_processor: AdvancedResonanceProcessor):
        self.resonance_processor = resonance_processor
        self.graph = nx.Graph()
        self.node_positions = {}  # Store positions for visualization

    def update_graph(self, patterns: list):
        """Update the graph based on detected patterns."""
        self.graph.clear()  # Clear the existing graph

        for pattern in patterns:
            self._add_pattern_to_graph(pattern)

    def _add_pattern_to_graph(self, pattern: dict):
        """Add a pattern to the graph."""
        pattern_id = self.resonance_processor.pattern_registry._generate_pattern_id(pattern)
        
        # Add pattern as a node
        self.graph.add_node(pattern_id, type=pattern['type'], timestamp=pattern['timestamp'])
        
        if 'dimensions' in pattern:
            for dim in pattern['dimensions']:
                dim_node = f"dim_{dim}"
                
                # Add dimension as a node if it doesn't exist
                if not self.graph.has_node(dim_node):
                    self.graph.add_node(dim_node, type='dimension')
                    
                # Connect pattern to its dimensions
                self.graph.add_edge(pattern_id, dim_node)

        # Connect patterns based on relationships
        if pattern['type'] == 'causal_pattern':
            cause_id = self.resonance_processor.pattern_registry._generate_pattern_id(pattern['cause'])
            effect_id = self.resonance_processor.pattern_registry._generate_pattern_id(pattern['effect'])
            self.graph.add_edge(cause_id, effect_id, type='causal')

    def analyze_graph(self) -> dict:
        """Analyze the graph to identify key structures and metrics."""
        analysis = {}

        # Basic metrics
        analysis['num_nodes'] = self.graph.number_of_nodes()
        analysis['num_edges'] = self.graph.number_of_edges()
        analysis['avg_degree'] = np.mean([d for _, d in self.graph.degree()]) if self.graph.number_of_nodes() > 0 else 0

        # Centrality measures
        analysis['degree_centrality'] = nx.degree_centrality(self.graph)
        analysis['betweenness_centrality'] = nx.betweenness_centrality(self.graph)
        analysis['closeness_centrality'] = nx.closeness_centrality(self.graph)
        analysis['eigenvector_centrality'] = nx.eigenvector_centrality_numpy(self.graph)

        # Community detection
        communities = nx.community.greedy_modularity_communities(self.graph)
        analysis['num_communities'] = len(communities)
        analysis['communities'] = communities

        return analysis
    
    def visualize_graph(self, layout: str = 'spring', save_to_file: bool = False, filename: str = 'graph.png'):
        """
        Visualize the graph using different layout algorithms.
        """
        if layout == 'spring':
            pos = nx.spring_layout(self.graph, seed=42)  # Using a seed for reproducibility
        elif layout == 'spectral':
            pos = nx.spectral_layout(self.graph)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(self.graph)
        elif layout == 'circular':
            pos = nx.circular_layout(self.graph)
        else:
            raise ValueError(f"Layout '{layout}' not recognized.")

        # Use stored positions if available, otherwise calculate new positions
        for node in self.graph.nodes():
            if node not in self.node_positions:
                self.node_positions[node] = pos[node]

        # Draw the graph
        nx.draw(self.graph, self.node_positions, with_labels=True, node_color='skyblue', node_size=800, edge_color='gray', font_size=10, font_weight='bold')

        # Save to file or show the plot
        if save_to_file:
            plt.savefig(filename)
        else:
            plt.show()

    def get_pattern_subgraph(self, pattern_type: str) -> nx.Graph:
        """
        Extract a subgraph containing only nodes of a specific pattern type.
        """
        nodes = [node for node, data in self.graph.nodes(data=True) if data.get('type') == pattern_type]
        return self.graph.subgraph(nodes)

    def get_dimension_subgraph(self, dimension: int) -> nx.Graph:
        """
        Extract a subgraph containing only nodes related to a specific dimension.
        """
        dim_node = f"dim_{dimension}"
        if not self.graph.has_node(dim_node):
            return nx.Graph()  # Return an empty graph if the dimension node doesn't exist

        nodes = [node for node in self.graph.nodes() if self.graph.has_edge(node, dim_node) or node == dim_node]
        return self.graph.subgraph(nodes)
    
    def get_state(self) -> dict:
        """Returns the current state of the graph engine."""
        return {
            'graph': {
                'nodes': list(self.graph.nodes(data=True)),
                'edges': list(self.graph.edges(data=True))
            },
            'analysis': self.analyze_graph()
        }
