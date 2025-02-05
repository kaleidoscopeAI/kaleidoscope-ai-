# modules/Visualizer.py
import networkx as nx
import matplotlib.pyplot as plt

class Visualizer:
    """Visualize node interactions and memory growth."""
    def __init__(self):
        self.graph = nx.Graph()

    def add_node(self, node_id, parent_id=None):
        """Add a node to the visualization."""
        self.graph.add_node(node_id)
        if parent_id:
            self.graph.add_edge(parent_id, node_id)

    def display(self):
        """Display the graph."""
        nx.draw(self.graph, with_labels=True, node_color='lightblue', font_weight='bold')
        plt.show()
