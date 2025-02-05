
from modules.NodeLifecycle import Node

class NodeSimulation:
    def __init__(self):
        self.nodes = []  # Store all active nodes

    def initialize_network(self, initial_nodes=3):
        """Initialize the network with a given number of nodes."""
        for i in range(initial_nodes):
            node_name = f"Node_{i+1}"
            attributes = {"energy": 100 + i * 10, "task": "general_processing"}
            node = Node(node_name, attributes)
            self.nodes.append(node)
        print(f"Initialized {initial_nodes} nodes.")

    def simulate_replication(self, cycles=2):
        """Simulate node replication over several cycles."""
        for cycle in range(cycles):
            print(f"--- Replication Cycle {cycle + 1} ---")
            new_nodes = []
            for node in self.nodes:
                # Each node replicates once per cycle
                child_node = node.replicate()
                new_nodes.append(child_node)
            self.nodes.extend(new_nodes)

    def simulate_specialization(self):
        """Specialize nodes based on their environment or task."""
        for node in self.nodes:
            if "child" in node.name:
                specialization_key = "environment"
                specialization_value = "finance" if "1" in node.name else "healthcare"
                node.specialize(specialization_key, specialization_value)

    def display_network(self):
        """Display all nodes and their attributes."""
        print(f"--- Current Network State ({len(self.nodes)} nodes) ---")
        for node in self.nodes:
            print(f"Node: {node.name}, Attributes: {node.attributes}")

# Example simulation execution
if __name__ == "__main__":
    simulation = NodeSimulation()
    simulation.initialize_network(initial_nodes=3)
    simulation.simulate_replication(cycles=2)
    simulation.simulate_specialization()
    simulation.display_network()
