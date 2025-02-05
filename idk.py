Python

import uuid
import time

class Node:
    def __init__(self, node_id: str, capacity: float, role: str, ip_address: str, port: int):
        self.node_id = node_id
        self.capacity = capacity  # Processing capacity
        self.role = role # i.e.: "kaleidoscope_core", "perspective_engine", "data_processing", "system_monitoring"
        self.status = "idle"  # Current status (e.g., "idle", "processing", "standby", "failed")
        self.last_heartbeat = time.time()
        self.tasks = []
        self.ip_address = ip_address
        self.port = port

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
            'tasks': self.tasks,
            'ip_address': self.ip_address,
            'port': self.port
        }

class NodeLifeCycleManager:
    def __init__(self):
        self.nodes = {}
        self.failed_nodes = {}

    def register_node(self, capacity: float, role: str, ip_address: str, port: int) -> str:
        """Register a new node with the system."""
        node_id = str(uuid.uuid4())
        new_node = Node(node_id, capacity, role, ip_address, port)
        self.nodes[node_id] = new_node
        return node_id

    def unregister_node(self, node_id: str):
        """Unregister a node from the system."""
        if node_id in self.nodes:
            del self.nodes[node_id]

    def get_node(self, node_id: str) -> Node:
        """Retrieve a node by its ID."""
        if node_id in self.nodes:
          return self.nodes[node_id]
        else:
          return None

    def update_node_status(self, node_id: str, status: str):
        """Update the status of a node."""
        if node_id in self.nodes:
            self.nodes[node_id].update_status(status)

    def monitor_nodes(self, heartbeat_interval: int = 10, failure_threshold: int = 30):
        """Monitor nodes and detect failures based on heartbeat."""
        current_time = time.time()
        for node_id, node in list(self.nodes.items()):
            if current_time - node.last_heartbeat > failure_threshold:
                print(f"Node {node_id} has not sent a heartbeat within the threshold. Marking as failed.")
                self.failed_nodes[node_id] = self.nodes.pop(node_id)
                self.failed_nodes[node_id].update_status("failed")

    def get_all_nodes(self, status_filter: str = None) -> list:
        """Retrieve all nodes, optionally filtered by status."""
        if status_filter:
            return [node.get_state() for node in self.nodes.values() if node.status == status_filter]
        else:
            return [node.get_state() for node in self.nodes.values()]

    def get_failed_nodes(self) -> list:
        """Retrieve all failed nodes."""
        return [node.get_state() for node in self.failed_nodes.values()]

    def assign_task_to_node(self, node_id: str, task: dict):
        """Assign a task to a specific node."""
        if node_id in self.nodes:
            self.nodes[node_id].assign_task(task)
        else:
            raise ValueError(f"Node with ID {node_id} not found.")
            
    def reassign_tasks(self, failed_node_id: str):
      """
      Reassign tasks from a failed node to other available nodes.
      """
      if failed_node_id in self.failed_nodes:
          failed_node = self.failed_nodes[failed_node_id]
          tasks = failed_node.tasks

          # Find available nodes with the same role
          available_nodes = [node for node in self.nodes.values() if node.role == failed_node.role and node.status == "idle"]

          if available_nodes:
              # Distribute tasks among available nodes
              for i, task in enumerate(tasks):
                  node_index = i % len(available_nodes)  # Cycle through available nodes
                  available_nodes[node_index].assign_task(task)
                  print(f"Task reassigned from failed node {failed_node_id} to node {available_nodes[node_index].node_id}")
          else:
              print(f"No available nodes with the same role to reassign tasks from failed node {failed_node_id}")

          # Clear the tasks list of the failed node
          failed_node.tasks = []
          
    def get_state(self) -> dict:
        """Return the current state of the node life cycle manager."""
        return {
            'nodes': {node_id: node.get_state() for node_id, node in self.nodes.items()},
            'failed_nodes': {node_id: node.get_state() for node_id, node in self.failed_nodes.items()}
        }
