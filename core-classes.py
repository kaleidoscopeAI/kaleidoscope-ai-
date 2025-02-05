# core/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import numpy as np
import networkx as nx
import logging

class BaseNode(ABC):
    """Abstract base class for all node types in the system."""
    
    def __init__(self, node_id: str, capacity: int = 100):
        self.node_id = node_id
        self.capacity = capacity
        self.energy = 100.0
        self.memory = []
        self.connections = []
        self.graph = nx.DiGraph()
        self.logger = logging.getLogger(f"Node-{node_id}")
        self.characteristics = {}
    
    @abstractmethod
    def process_data(self, data: Any) -> Dict:
        """Process incoming data and generate insights."""
        pass

    @abstractmethod
    def update_state(self):
        """Update internal state based on current conditions."""
        pass

    def connect_to(self, other_node: 'BaseNode'):
        """Establish connection with another node."""
        if other_node not in self.connections:
            self.connections.append(other_node)
            self.graph.add_edge(self.node_id, other_node.node_id)
            self.logger.info(f"Connected to node {other_node.node_id}")

    def consume_energy(self, amount: float):
        """Consume energy for operations."""
        self.energy = max(0.0, self.energy - amount)
        if self.energy < 20.0:
            self.logger.warning(f"Low energy level: {self.energy}")

    def receive_energy(self, amount: float):
        """Receive energy from the system."""
        self.energy = min(100.0, self.energy + amount)

    def store_in_memory(self, data: Any):
        """Store data in node memory."""
        if len(self.memory) >= self.capacity:
            self.memory.pop(0)  # Remove oldest memory
        self.memory.append(data)

    def get_state(self) -> Dict:
        """Return current state of the node."""
        return {
            "node_id": self.node_id,
            "energy": self.energy,
            "memory_usage": len(self.memory) / self.capacity,
            "connections": len(self.connections),
            "characteristics": self.characteristics
        }

class BaseNetwork(ABC):
    """Abstract base class for all networks in the system."""
    
    def __init__(self):
        self.nodes = []
        self.network = nx.Graph()
        self.energy_pool = 1000.0
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def add_node(self, node: BaseNode):
        """Add a node to the network."""
        pass

    @abstractmethod
    def process_data(self, data: Any) -> Dict:
        """Process data through the network."""
        pass

    def distribute_energy(self):
        """Distribute energy among nodes."""
        active_nodes = [node for node in self.nodes if node.energy < 100.0]
        if not active_nodes:
            return

        total_deficit = sum(100.0 - node.energy for node in active_nodes)
        if total_deficit <= 0:
            return

        for node in active_nodes:
            deficit = 100.0 - node.energy
            share = (deficit / total_deficit) * min(self.energy_pool, total_deficit)
            node.receive_energy(share)
            self.energy_pool -= share

    def connect_nodes(self, node1_id: str, node2_id: str):
        """Connect two nodes in the network."""
        node1 = next((n for n in self.nodes if n.node_id == node1_id), None)
        node2 = next((n for n in self.nodes if n.node_id == node2_id), None)
        
        if node1 and node2:
            node1.connect_to(node2)
            node2.connect_to(node1)
            self.network.add_edge(node1_id, node2_id)
            self.logger.info(f"Connected nodes {node1_id} and {node2_id}")
        else:
            self.logger.error(f"Failed to connect nodes {node1_id} and {node2_id}")

    def get_network_state(self) -> Dict:
        """Return current state of the network."""
        return {
            "node_count": len(self.nodes),
            "edge_count": self.network.number_of_edges(),
            "energy_pool": self.energy_pool,
            "nodes": [node.get_state() for node in self.nodes]
        }

class SystemMonitor:
    """Monitors and logs system performance and state."""
    
    def __init__(self):
        self.logger = logging.getLogger("SystemMonitor")
        self.metrics = {
            "energy_usage": [],
            "memory_usage": [],
            "processing_time": [],
            "node_count": []
        }
        self.alerts = []

    def record_metric(self, metric_name: str, value: float):
        """Record a metric value."""
        if metric_name in self.metrics:
            self.metrics[metric_name].append(value)
            if len(self.metrics[metric_name]) > 1000:
                self.metrics[metric_name] = self.metrics[metric_name][-1000:]

    def check_thresholds(self, network: BaseNetwork):
        """Check system thresholds and generate alerts."""
        if network.energy_pool < 200.0:
            self.alerts.append({
                "level": "WARNING",
                "message": "Low energy pool",
                "value": network.energy_pool
            })
            self.logger.warning(f"Low energy pool: {network.energy_pool}")

        for node in network.nodes:
            if node.energy < 10.0:
                self.alerts.append({
                    "level": "CRITICAL",
                    "message": f"Critical energy level in node {node.node_id}",
                    "value": node.energy
                })
                self.logger.critical(f"Critical energy level in node {node.node_id}: {node.energy}")

    def get_system_health(self) -> Dict:
        """Return overall system health status."""
        return {
            "metrics": {k: np.mean(v) if v else 0 for k, v in self.metrics.items()},
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "status": "HEALTHY" if len(self.alerts) < 3 else "WARNING"
        }
