# File: energy_flow_visualization.py

import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict

class EnergyFlowVisualizer:
    """
    Visualizes energy flow between nodes during redistribution.
    """
    def __init__(self, nodes: Dict[str, Dict[str, float]], edges: Dict[Tuple[str, str], float]):
        """
        Initializes the energy flow visualizer.

        Parameters:
            nodes (Dict[str, Dict[str, float]]): A dictionary of nodes and their metrics.
            edges (Dict[Tuple[str, str], float]): A dictionary of energy transfer edges with weights.
        """
        self.nodes = nodes
        self.edges = edges
        self.graph = nx.DiGraph()

        # Add nodes and edges to the graph
        for node_id, metrics in nodes.items():
            self.graph.add_node(node_id, energy=metrics["energy"])

        for (source, target), weight in edges.items():
            self.graph.add_edge(source, target, weight=weight)

    def visualize(self):
        """
        Visualizes the energy flow graph.
        """
        pos = nx.spring_layout(self.graph)  # Position nodes using a force-directed layout

        # Node sizes based on energy levels
        node_sizes = [self.graph.nodes[node]["energy"] * 10 for node in self.graph.nodes()]

        # Edge widths based on energy transfer weights
        edge_weights = [self.graph[u][v]["weight"] for u, v in self.graph.edges()]

        plt.figure(figsize=(12, 12))
        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            node_size=node_sizes,
            font_weight="bold",
            node_color="skyblue",
            edge_color="gray",
            width=edge_weights
        )
        nx.draw_networkx_edge_labels(
            self.graph,
            pos,
            edge_labels={(u, v): f"{d['weight']}" for u, v, d in self.graph.edges(data=True)}
        )
        plt.title("Energy Flow Visualization")
        plt.show()

# Example Usage
if __name__ == "__main__":
    # Example nodes and energy transfers
    nodes = {
        "Node-1": {"energy": 90.0},
        "Node-2": {"energy": 20.0},
        "Node-3": {"energy": 50.0},
        "Node-4": {"energy": 70.0}
    }

    edges = {
        ("Node-1", "Node-2"): 15.0,
        ("Node-3", "Node-4"): 10.0,
        ("Node-4", "Node-2"): 5.0
    }

    # Initialize the visualizer
    visualizer = EnergyFlowVisualizer(nodes, edges)

    # Visualize the energy flow
    visualizer.visualize()
