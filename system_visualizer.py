system_monitoring/visualization/system_visualizer.py
Python

import networkx as nx
import matplotlib.pyplot as plt
import time

class SystemVisualizer:
    def __init__(self, node_manager: NodeLifeCycleManager):
        self.node_manager = node_manager
        self.graph = nx.Graph()
        self.positions = {}  # Store positions for nodes
        self.last_update = time.time()

    def update_graph(self):
        """Update the graph based on the current system state."""
        self.graph.clear()
        self.positions.clear()

        # Add nodes to the graph
        for node_id, node in self.node_manager.nodes.items():
            self.graph.add_node(node_id, status=node.status, role=node.role)

        # Add failed nodes to the graph
        for node_id, node in self.node_manager.failed_nodes.items():
            self.graph.add_node(node_

_id, status=node.status, role=node.role)

        # Define positions for different roles (for visualization)
        role_positions = {
            "kaleidoscope_core": (0, 0),
            "perspective_engine": (1, 1),
            "data_processing": (1, -1),
            "system_monitoring": (-1, -1),
            "auxiliary": (-1, 1),
            "failed": (0, -2)
        }

        # Calculate positions for nodes
        for node_id, node_data in self.graph.nodes(data=True):
            role = node_data['role']
            if role in role_positions:
                if role not in self.positions:
                    self.positions[role] = list(role_positions[role])
                else:
                    # Increment position for nodes with the same role
                    self.positions[role][0] += 0.2 
                    self.positions[role][1] += 0.2
                self.positions[node_id] = tuple(self.positions[role])
            else:
                # Default position for unknown roles
                self.positions[node_id] = (0, 0)

        self.last_update = time.time()

    def visualize_system(self, save_to_file: bool = False, filename: str = 'system_visualization.png'):
        """Visualize the system state."""
        self.update_graph()

        # Draw the graph
        node_colors = ['lightgreen' if data['status'] == 'idle' else 'red' if data['status'] == 'failed' else 'skyblue' for node, data in self.graph.nodes(data=True)]
        nx.draw(self.graph, self.positions, with_labels=True, node_color=node_colors, node_size=1000, font_size=10)

        # Add labels for roles
        for role, pos in self.positions.items():
            if isinstance(role, str):  # Check if the key is a role name
                plt.text(pos[0], pos[1] - 0.2, role, horizontalalignment='center', fontsize=12, fontweight='bold')

        # Save to file or show the plot
        if save_to_file:
            plt.savefig(filename)
            plt.close()
        else:
            plt.show()
            
    def get_state(self) -> dict:
        """Returns the current state of the system visualizer."""
        return {
            'graph': {
                'nodes': list(self.graph.nodes(data=True)),
                'edges': list(self.graph.edges(data=True))
            },
            'positions': self.positions,
            'last_update': self.last_update
        }
