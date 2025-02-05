node_management/failsafe/failure_detection.py
Python

import time

class FailureDetector:
    def __init__(self, node_manager: NodeLifeCycleManager, heartbeat_interval: int = 10, failure_threshold: int = 30):
        self.node_manager = node_manager
        self.heartbeat_interval = heartbeat_interval
        self.failure_threshold = failure_threshold
        self.last_check = time.time()

    def detect_failures(self):
        """Detect node failures based on heartbeat."""
        current_time = time.time()
        if current_time - self.last_check >= self.heartbeat_interval:
            for node_id, node in list(self.node_manager.nodes.items()):
                if current_time - node.last_heartbeat > self.failure_threshold:
                    print(f"Node {node_id} has not sent a heartbeat within the threshold. Marking as failed.")
                    self.node_manager.failed_nodes[node_id] = self.node_manager.nodes.pop(node_id)
                    self.node_manager.failed_nodes[node_id].update_status("failed")
            self.last_check = current_time
            
    def get_state(self) -> dict:
        """Returns the current state of the failure detector."""
        return {
            'heartbeat_interval': self.heartbeat_interval,
            'failure_threshold': self.failure_threshold,
            'last_check': self.last_check
        }
