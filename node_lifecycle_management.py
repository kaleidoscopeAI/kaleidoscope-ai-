# File: node_lifecycle_management.py

from typing import Dict, List
from datetime import datetime
import logging
import numpy as np

# Configure logging
logging.basicConfig(
    filename="node_lifecycle.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Node:
    def __init__(self, node_id: str, energy: float, knowledge: float, role: str = "general"):
        self.node_id = node_id
        self.energy = energy
        self.knowledge = knowledge
        self.role = role  # New: Assign specific roles to nodes
        self.creation_time = datetime.now()
        self.last_active = datetime.now()
        self.status = "active"  # Status can be "active", "inactive", or "retired"

    def update_activity(self):
        """Updates the node's last active time."""
        self.last_active = datetime.now()

    def deactivate(self):
        """Deactivates the node."""
        self.status = "inactive"
        logging.info(f"Node {self.node_id} deactivated.")

    def reactivate(self):
        """Reactivates the node."""
        self.status = "active"
        logging.info(f"Node {self.node_id} reactivated.")

    def retire(self):
        """Retires the node permanently."""
        self.status = "retired"
        logging.info(f"Node {self.node_id} retired.")

class NodeLifecycleManager:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.history: List[Dict] = []  # New: Maintain a history of node states

    def add_node(self, node_id: str, energy: float, knowledge: float, role: str = "general"):
        """Adds a new node to the system."""
        if node_id in self.nodes:
            logging.warning(f"Node {node_id} already exists.")
            return

        self.nodes[node_id] = Node(node_id, energy, knowledge, role)
        logging.info(f"Node {node_id} added with energy {energy}, knowledge {knowledge}, role {role}.")

    def remove_node(self, node_id: str):
        """Removes a node from the system."""
        if node_id in self.nodes:
            self.history.append({
                "node_id": node_id,
                "status": "removed",
                "timestamp": datetime.now()
            })
            del self.nodes[node_id]
            logging.info(f"Node {node_id} removed from the system.")
        else:
            logging.warning(f"Attempted to remove non-existent node {node_id}.")

    def deactivate_node(self, node_id: str):
        """Deactivates a node."""
        if node_id in self.nodes:
            self.nodes[node_id].deactivate()
        else:
            logging.warning(f"Attempted to deactivate non-existent node {node_id}.")

    def reactivate_node(self, node_id: str):
        """Reactivates a node."""
        if node_id in self.nodes:
            self.nodes[node_id].reactivate()
        else:
            logging.warning(f"Attempted to reactivate non-existent node {node_id}.")

    def retire_node(self, node_id: str):
        """Retires a node permanently."""
        if node_id in self.nodes:
            self.history.append({
                "node_id": node_id,
                "status": "retired",
                "timestamp": datetime.now()
            })
            self.nodes[node_id].retire()
        else:
            logging.warning(f"Attempted to retire non-existent node {node_id}.")

    def list_nodes(self):
        """Lists all nodes and their statuses."""
        for node_id, node in self.nodes.items():
            logging.info(f"Node {node_id}: Status={node.status}, Energy={node.energy}, Knowledge={node.knowledge}, Role={node.role}")
        return {node_id: node.status for node_id, node in self.nodes.items()}

    def check_inactive_nodes(self, threshold_minutes: int):
        """Checks for nodes that have been inactive beyond a threshold and deactivates them."""
        now = datetime.now()
        for node_id, node in self.nodes.items():
            if node.status == "active" and (now - node.last_active).total_seconds() > threshold_minutes * 60:
                node.deactivate()
                logging.info(f"Node {node_id} deactivated due to inactivity.")

    def migrate_resources(self, source_node_id: str, target_node_id: str):
        """Transfers resources from one node to another."""
        if source_node_id in self.nodes and target_node_id in self.nodes:
            source = self.nodes[source_node_id]
            target = self.nodes[target_node_id]

            # Transfer half of the source's resources
            transfer_energy = source.energy * 0.5
            transfer_knowledge = source.knowledge * 0.5

            source.energy -= transfer_energy
            source.knowledge -= transfer_knowledge
            target.energy += transfer_energy
            target.knowledge += transfer_knowledge

            logging.info(f"Transferred {transfer_energy} energy and {transfer_knowledge} knowledge from {source_node_id} to {target_node_id}.")
        else:
            logging.warning(f"Migration failed: Nodes {source_node_id} or {target_node_id} do not exist.")

    def check_health(self, threshold_energy: float = 20.0, threshold_knowledge: float = 10.0):
        """Checks the health of all nodes and flags low-performing ones."""
        for node_id, node in self.nodes.items():
            if node.energy < threshold_energy or node.knowledge < threshold_knowledge:
                logging.warning(f"Node {node_id} is unhealthy: Energy={node.energy}, Knowledge={node.knowledge}.")

# Example Usage
if __name__ == "__main__":
    manager = NodeLifecycleManager()

    # Adding nodes
    manager.add_node("Node-1", energy=80, knowledge=50, role="computation")
    manager.add_node("Node-2", energy=60, knowledge=40, role="storage")

    # Listing nodes
    print("Nodes:", manager.list_nodes())

    # Deactivating a node
    manager.deactivate_node("Node-1")

    # Reactivating a node
    manager.reactivate_node("Node-1")

    # Retiring a node
    manager.retire_node("Node-2")

    # Checking inactive nodes
    manager.check_inactive_nodes(threshold_minutes=1)

    # Resource migration
    manager.migrate_resources("Node-1", "Node-2")

    # Checking node health
    manager.check_health(threshold_energy=50, threshold_knowledge=30)

    # Removing a node
    manager.remove_node("Node-1")
