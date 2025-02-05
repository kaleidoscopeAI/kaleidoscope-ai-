import threading
import time
import queue
from typing import Dict, Any, Callable

class NodeCommunication:
    """
    Handles communication between nodes, task delegation, and error feedback.
    """

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.message_queue = queue.Queue()
        self.active_nodes: Dict[str, Callable] = {}  # Node registry: node_id -> callback function
        self.heartbeat_interval = 2  # seconds

        # Start heartbeat monitoring
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_signal, daemon=True)
        self._heartbeat_thread.start()

    def register_node(self, node_id: str, callback: Callable):
        """
        Registers a node's callback function for communication.
        :param node_id: Unique ID of the node.
        :param callback: Function to handle incoming messages.
        """
        if node_id not in self.active_nodes:
            self.active_nodes[node_id] = callback
            print(f"[{self.node_id}] Node '{node_id}' registered successfully.")
        else:
            print(f"[{self.node_id}] Node '{node_id}' is already registered.")

    def send_message(self, target_node_id: str, message: Dict[str, Any]):
        """
        Sends a message to a specific node.
        :param target_node_id: The ID of the recipient node.
        :param message: The message payload.
        """
        if target_node_id in self.active_nodes:
            try:
                print(f"[{self.node_id}] Sending message to '{target_node_id}': {message}")
                self.active_nodes[target_node_id](message)  # Call the target node's callback
            except Exception as e:
                print(f"[{self.node_id}] Error sending message to '{target_node_id}': {e}")
        else:
            print(f"[{self.node_id}] Node '{target_node_id}' is not registered.")

    def receive_message(self, message: Dict[str, Any]):
        """
        Receives a message and adds it to the processing queue.
        :param message: The incoming message payload.
        """
        print(f"[{self.node_id}] Message received: {message}")
        self.message_queue.put(message)

    def process_messages(self):
        """
        Processes all messages in the queue.
        """
        while not self.message_queue.empty():
            message = self.message_queue.get()
            print(f"[{self.node_id}] Processing message: {message}")
            # Simulate message handling logic
            if message.get("type") == "task":
                self._handle_task(message)
            elif message.get("type") == "error":
                self._handle_error(message)
            else:
                print(f"[{self.node_id}] Unknown message type: {message}")

    def _handle_task(self, message: Dict[str, Any]):
        print(f"[{self.node_id}] Task received: {message.get('task')}")

    def _handle_error(self, message: Dict[str, Any]):
        print(f"[{self.node_id}] Error feedback received: {message.get('error')}")

    def _heartbeat_signal(self):
        """
        Sends periodic heartbeat signals.
        """
        while True:
            print(f"[{self.node_id}] Heartbeat signal - Node is active.")
            time.sleep(self.heartbeat_interval)

# Example Usage
if __name__ == "__main__":
    def node_callback(message):
        print(f"[Node B] Callback received message: {message}")

    # Initialize Node A and Node B
    node_a = NodeCommunication("Node_A")
    node_b = NodeCommunication("Node_B")

    # Register Node B's callback in Node A's registry
    node_a.register_node("Node_B", node_callback)

    # Send messages
    node_a.send_message("Node_B", {"type": "task", "task": "Analyze Titanic data"})
    node_a.send_message("Node_B", {"type": "error", "error": "Memory bank full"})

    # Process Node A's incoming messages
    node_a.receive_message({"type": "task", "task": "Explore iceberg patterns"})
    node_a.process_messages()

    # Keep the nodes alive to monitor heartbeats
    time.sleep(10)
