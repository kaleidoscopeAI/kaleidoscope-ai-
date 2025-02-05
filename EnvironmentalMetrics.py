import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from collections import deque
from datetime import datetime
from typing import Dict, List

class NodeMetrics:
    """
    Tracks individual node performance metrics.
    """
    def __init__(self):
        self.energy_history = deque(maxlen=1000)
        self.knowledge_history = deque(maxlen=1000)
        self.task_completion_rate = deque(maxlen=1000)
        self.interaction_count = 0
        self.last_active = datetime.now()
        self.performance_score = 0.0

class EnvironmentalMetrics:
    """
    Tracks and visualizes the metrics for the Kaleidoscope AI environment using multidimensional graph theory.
    """

    def __init__(self):
        self.data_inflow = deque(maxlen=1000)  # Tracks inflow of data into the environment
        self.nodes_in_environment = deque(maxlen=1000)  # Tracks number of active nodes
        self.energy_levels = deque(maxlen=1000)  # Tracks system-wide energy levels
        self.resource_levels = deque(maxlen=1000)  # Tracks available resources
        self.insight_counts = deque(maxlen=1000)  # Tracks insights generated
        self.graph = nx.DiGraph()  # Initializes a directed graph for nodes and tasks
        self.node_metrics: Dict[str, NodeMetrics] = {}  # Tracks performance metrics for each node

    def add_node(self, node_id, energy_level, knowledge):
        """
        Adds a node to the graph and initializes its metrics.

        Parameters:
            node_id (str): Unique identifier for the node.
            energy_level (float): Initial energy level of the node.
            knowledge (float): Initial knowledge level of the node.
        """
        self.graph.add_node(node_id, energy=energy_level, knowledge=knowledge)
        self.node_metrics[node_id] = NodeMetrics()
        self.node_metrics[node_id].energy_history.append(energy_level)
        self.node_metrics[node_id].knowledge_history.append(knowledge)

    def add_task_dependency(self, source_node, target_node, weight):
        """
        Adds a directed edge to represent a task dependency between nodes.

        Parameters:
            source_node (str): Node initiating the task.
            target_node (str): Node receiving the task.
            weight (float): Complexity or cost of the task.
        """
        self.graph.add_edge(source_node, target_node, weight=weight)
        self.node_metrics[source_node].interaction_count += 1
        self.node_metrics[target_node].interaction_count += 1

    def update_metrics(self, data_inflow, node_count, energy_level, resource_level, insights):
        """
        Updates the environmental metrics with the latest data.

        Parameters:
            data_inflow (int): Number of datasets entering the environment.
            node_count (int): Number of active nodes.
            energy_level (float): Total system-wide energy.
            resource_level (float): Available resources in the system.
            insights (int): Insights generated during this time period.
        """
        self.data_inflow.append(data_inflow)
        self.nodes_in_environment.append(node_count)
        self.energy_levels.append(energy_level)
        self.resource_levels.append(resource_level)
        self.insight_counts.append(insights)

    def calculate_node_performance(self, node_id):
        """
        Calculates a performance score for a specific node.

        Parameters:
            node_id (str): Unique identifier for the node.

        Returns:
            float: Performance score of the node.
        """
        if node_id not in self.node_metrics:
            return 0.0

        metrics = self.node_metrics[node_id]
        avg_energy = np.mean(list(metrics.energy_history)) if metrics.energy_history else 0
        avg_knowledge = np.mean(list(metrics.knowledge_history)) if metrics.knowledge_history else 0
        interaction_score = metrics.interaction_count / max(1, len(metrics.energy_history))

        performance_score = 0.4 * avg_energy + 0.4 * avg_knowledge + 0.2 * interaction_score
        metrics.performance_score = performance_score
        return performance_score

    def plot_metrics(self):
        """
        Plots the tracked environmental metrics.
        """
        plt.figure(figsize=(15, 10))

        # Data inflow
        plt.subplot(2, 2, 1)
        plt.plot(self.data_inflow, label='Data Inflow')
        plt.title('Data Inflow Over Time')
        plt.xlabel('Time Steps')
        plt.ylabel('Data Count')
        plt.legend()

        # Nodes in environment
        plt.subplot(2, 2, 2)
        plt.plot(self.nodes_in_environment, label='Active Nodes', color='orange')
        plt.title('Active Nodes Over Time')
        plt.xlabel('Time Steps')
        plt.ylabel('Node Count')
        plt.legend()

        # Energy levels
        plt.subplot(2, 2, 3)
        plt.plot(self.energy_levels, label='Energy Levels', color='green')
        plt.title('System-Wide Energy Levels')
        plt.xlabel('Time Steps')
        plt.ylabel('Energy')
        plt.legend()

        # Insights generated
        plt.subplot(2, 2, 4)
        plt.plot(self.insight_counts, label='Insights Generated', color='purple')
        plt.title('Insights Over Time')
        plt.xlabel('Time Steps')
        plt.ylabel('Insight Count')
        plt.legend()

        plt.tight_layout()
        plt.show()

    def visualize_graph(self):
        """
        Visualizes the node interaction graph with advanced customizations.
        """
        pos = nx.spring_layout(self.graph)  # Position nodes using a force-directed layout
        node_sizes = [self.graph.nodes[node]['energy'] * 10 for node in self.graph.nodes]
        node_colors = [plt.cm.viridis(self.graph.nodes[node]['knowledge'] / 100) for node in self.graph.nodes]
        edge_weights = nx.get_edge_attributes(self.graph, 'weight')

        plt.figure(figsize=(12, 12))
        nx.draw(
            self.graph, pos, with_labels=True, node_size=node_sizes, font_weight='bold',
            node_color=node_colors, edge_color='gray'
        )
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_weights)
        plt.title('Node Interaction Graph')
        plt.show()

# Example Usage
environment_metrics = EnvironmentalMetrics()

# Simulating node additions and interactions
for i in range(5):
    environment_metrics.add_node(f"Node-{i}", energy_level=np.random.uniform(50, 100), knowledge=np.random.uniform(10, 50))

# Adding task dependencies
for i in range(4):
    environment_metrics.add_task_dependency(f"Node-{i}", f"Node-{i+1}", weight=np.random.uniform(5, 20))

# Simulating data updates for 100 time steps
for t in range(100):
    environment_metrics.update_metrics(
        data_inflow=np.random.randint(50, 100),
        node_count=5,
        energy_level=np.random.uniform(200, 1000),
        resource_level=np.random.uniform(500, 1500),
        insights=np.random.randint(10, 30)
    )

# Plot the metrics
environment_metrics.plot_metrics()

# Visualize the graph
environment_metrics.visualize_graph()
