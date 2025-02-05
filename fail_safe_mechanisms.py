# File: fail_safe_mechanisms.py

import logging
from typing import Dict
import time

# Configure logging
logging.basicConfig(
    filename="fail_safe_mechanisms.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Node:
    """
    Represents a node in the system with basic energy and status management.
    """
    def __init__(self, node_id: str, energy: float):
        self.node_id = node_id
        self.energy = energy
        self.status = "active"  # Status can be "active", "inactive", or "failed"

    def deactivate(self):
        self.status = "inactive"
        logging.warning(f"Node {self.node_id} deactivated.")

    def fail(self):
        self.status = "failed"
        logging.error(f"Node {self.node_id} has failed.")

    def recover(self):
        if self.status == "failed":
            self.status = "active"
            self.energy = max(20, self.energy)  # Restore minimum energy
            logging.info(f"Node {self.node_id} recovered and reactivated.")

class FailSafeManager:
    """
    Manages fail-safe mechanisms to handle node failures and ensure system stability.
    """
    def __init__(self, nodes: Dict[str, Node]):
        self.nodes = nodes

    def monitor_nodes(self):
        """
        Monitors nodes for failure conditions and logs anomalies.
        """
        for node_id, node in self.nodes.items():
            if node.energy < 10:
                logging.warning(f"Node {node_id} has critically low energy ({node.energy}).")
                node.deactivate()

    def recover_failed_nodes(self):
        """
        Attempts to recover failed nodes.
        """
        for node_id, node in self.nodes.items():
            if node.status == "failed":
                node.recover()
                logging.info(f"Node {node_id} recovery attempted.")

    def shutdown(self):
        """
        Gracefully shuts down the system by deactivating all nodes.
        """
        for node_id, node in self.nodes.items():
            node.deactivate()
        logging.info("System shutdown completed. All nodes deactivated.")

    def restart_system(self):
        """
        Restarts the system by reactivating all inactive nodes.
        """
        for node_id, node in self.nodes.items():
            if node.status == "inactive":
                node.status = "active"
                logging.info(f"Node {node_id} reactivated during system restart.")
        logging.info("System restart completed. All nodes reactivated.")

# Example Usage
if __name__ == "__main__":
    # Initialize nodes
    nodes = {
        "Node-1": Node("Node-1", energy=50),
        "Node-2": Node("Node-2", energy=5),
        "Node-3": Node("Node-3", energy=20),
        "Node-4": Node("Node-4", energy=0)
    }

    # Initialize the fail-safe manager
    manager = FailSafeManager(nodes)

    # Monitor nodes for failures
    manager.monitor_nodes()

    # Attempt to recover failed nodes
    manager.recover_failed_nodes()

    # Simulate system shutdown
    time.sleep(2)
    manager.shutdown()

    # Simulate system restart
    time.sleep(2)
    manager.restart_system()

    # Print final node statuses
    for node_id, node in nodes.items():
        print(f"{node_id}: Status={node.status}, Energy={node.energy}")
