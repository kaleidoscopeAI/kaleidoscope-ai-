import heapq
from typing import Dict, List

class AdaptiveEnergyFlow:
    """
    Optimizes energy distribution across nodes in the Kaleidoscope AI system.
    Ensures efficient use of energy by redistributing resources based on task needs and thresholds.
    """

    def __init__(self):
        self.node_energy: Dict[str, float] = {}  # Stores energy levels for each node
        self.priority_queue: List[tuple] = []  # Min-heap to manage redistribution priorities

    def add_node(self, node_id: str, initial_energy: float):
        """
        Adds a new node with its initial energy level.
        :param node_id: Unique identifier for the node.
        :param initial_energy: Starting energy level for the node.
        """
        self.node_energy[node_id] = initial_energy
        heapq.heappush(self.priority_queue, (initial_energy, node_id))
        print(f"Node '{node_id}' added with energy {initial_energy}.")

    def remove_node(self, node_id: str):
        """
        Removes a node from the energy flow system.
        :param node_id: Unique identifier for the node to remove.
        """
        if node_id in self.node_energy:
            del self.node_energy[node_id]
            self.priority_queue = [(e, n) for e, n in self.priority_queue if n != node_id]
            heapq.heapify(self.priority_queue)
            print(f"Node '{node_id}' removed from the energy system.")

    def redistribute_energy(self, energy_threshold: float = 50.0):
        """
        Redistributes energy between nodes to ensure balance.
        Nodes below the threshold receive energy from higher-energy nodes.
        :param energy_threshold: Minimum energy level required for a node.
        """
        nodes_below_threshold = [n for n, e in self.node_energy.items() if e < energy_threshold]
        nodes_above_threshold = [n for n, e in self.node_energy.items() if e > energy_threshold]

        if not nodes_below_threshold or not nodes_above_threshold:
            print("No energy redistribution required.")
            return

        # Calculate total energy deficit
        total_deficit = sum(energy_threshold - self.node_energy[n] for n in nodes_below_threshold)
        donors = sorted(nodes_above_threshold, key=lambda n: self.node_energy[n], reverse=True)

        for donor in donors:
            donor_energy = self.node_energy[donor]
            if donor_energy <= energy_threshold:
                continue

            donation = min(donor_energy - energy_threshold, total_deficit)
            self.node_energy[donor] -= donation
            total_deficit -= donation

            for recipient in nodes_below_threshold:
                if self.node_energy[recipient] < energy_threshold:
                    needed = energy_threshold - self.node_energy[recipient]
                    transferred = min(needed, donation)
                    self.node_energy[recipient] += transferred
                    donation -= transferred

            if total_deficit <= 0:
                break

        heapq.heapify(self.priority_queue)
        print("Energy redistribution completed.")

    def prioritize_node(self, node_id: str, priority_factor: float):
        """
        Adjusts a node's priority for receiving energy based on a factor.
        Higher factors indicate higher priority.
        :param node_id: Unique identifier for the node.
        :param priority_factor: The factor to apply to the node's energy priority.
        """
        if node_id in self.node_energy:
            current_energy = self.node_energy[node_id]
            adjusted_energy = current_energy * priority_factor
            self.priority_queue = [(e, n) if n != node_id else (adjusted_energy, n) for e, n in self.priority_queue]
            heapq.heapify(self.priority_queue)
            print(f"Node '{node_id}' priority adjusted by factor {priority_factor}.")

    def get_node_energy(self, node_id: str) -> float:
        """
        Retrieves the current energy level of a node.
        :param node_id: Unique identifier for the node.
        :return: Current energy level of the node.
        """
        return self.node_energy.get(node_id, 0.0)

    def display_energy_levels(self):
        """
        Displays the current energy levels of all nodes.
        """
        print("Current Node Energy Levels:")
        for node, energy in self.node_energy.items():
            print(f"Node {node}: {energy:.2f}")

# Example usage
if __name__ == "__main__":
    # Initialize the Adaptive Energy Flow system
    energy_flow = AdaptiveEnergyFlow()

    # Add nodes
    energy_flow.add_node("Node1", 40.0)
    energy_flow.add_node("Node2", 100.0)
    energy_flow.add_node("Node3", 30.0)

    # Display energy levels
    energy_flow.display_energy_levels()

    # Redistribute energy
    energy_flow.redistribute_energy(energy_threshold=50.0)
    energy_flow.display_energy_levels()

    # Adjust priority
    energy_flow.prioritize_node("Node1", 1.5)
    energy_flow.display_energy_levels()
