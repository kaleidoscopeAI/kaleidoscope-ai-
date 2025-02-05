# File: dynamic_thresholds.py

import logging
from typing import Dict

# Configure logging
logging.basicConfig(
    filename="dynamic_thresholds.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class DynamicThresholdManager:
    """
    Manages dynamic thresholds for energy optimization based on system metrics.
    """
    def __init__(self, nodes: Dict[str, Dict[str, float]]):
        """
        Initializes the threshold manager.

        Parameters:
            nodes (Dict[str, Dict[str, float]]): A dictionary of nodes and their metrics.
        """
        self.nodes = nodes
        self.high_energy_threshold = 70.0
        self.low_energy_threshold = 30.0
        self.utilization_threshold = 50.0

    def adjust_thresholds(self, task_queue_length: int, avg_energy: float):
        """
        Adjusts thresholds dynamically based on system metrics.

        Parameters:
            task_queue_length (int): The length of the current task queue.
            avg_energy (float): The average energy level of all nodes.
        """
        if task_queue_length > 10:
            self.low_energy_threshold = max(20.0, self.low_energy_threshold - 5.0)
            self.high_energy_threshold = min(80.0, self.high_energy_threshold + 5.0)
        elif avg_energy > 60:
            self.low_energy_threshold = min(40.0, self.low_energy_threshold + 5.0)
            self.high_energy_threshold = max(60.0, self.high_energy_threshold - 5.0)

        logging.info(
            f"Adjusted thresholds: Low={self.low_energy_threshold}, High={self.high_energy_threshold}"
        )

    def get_thresholds(self) -> Dict[str, float]:
        """
        Returns the current thresholds.

        Returns:
            Dict[str, float]: The current high and low energy thresholds.
        """
        return {
            "low_energy_threshold": self.low_energy_threshold,
            "high_energy_threshold": self.high_energy_threshold
        }

# Example Usage
if __name__ == "__main__":
    # Example nodes with metrics
    nodes = {
        "Node-1": {"energy": 90.0},
        "Node-2": {"energy": 20.0},
        "Node-3": {"energy": 50.0},
        "Node-4": {"energy": 70.0}
    }

    # Initialize the threshold manager
    manager = DynamicThresholdManager(nodes)

    # Simulate adjustments
    for i in range(5):
        avg_energy = sum(node["energy"] for node in nodes.values()) / len(nodes)
        manager.adjust_thresholds(task_queue_length=i * 5, avg_energy=avg_energy)

        # Print the updated thresholds
        print(manager.get_thresholds())
