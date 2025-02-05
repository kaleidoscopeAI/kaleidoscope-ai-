node_management/core/node_lifecycle.py
Python

import uuid
import time

class Node:
    def __init__(self, node_id: str, capacity: float, role: str):
        self.node_id = node_id
        self.capacity = capacity  # Processing capacity
        self.role = role # i.e.: "kaleidoscope_core", "perspective_engine", "data_processing", "system_monitoring"
        self.status = "idle"  # Current status (e.g., "idle", "processing", "standby", "failed")
        self.last_heartbeat = time.time()
        self.tasks = []

    def assign_task(self, task: dict):
        """Assign a task to the node."""
        self.tasks.append(task)
        self.status = "processing"

    def update_status(self, status: str):
        """Update the node's status."""
        self.status = status

    def send_heartbeat(self):
        """Send a heartbeat signal to indicate the node is alive."""
        self.last_heartbeat = time.time()

    def get_state(self) -> dict:
        """Return the current state of the node."""
        return {
            'node_id': self.node_id,
            'capacity': self.capacity,
            'role': self.role,
            'status': self.status,
            'last_heartbeat': self.last_heartbeat,
            'tasks': self.tasks
        }

class NodeLifeCycleManager:
    def __init__(self):
        self.nodes = {}
        self.failed_nodes = {}

    def register_node(self, capacity: float, role: str) ->
