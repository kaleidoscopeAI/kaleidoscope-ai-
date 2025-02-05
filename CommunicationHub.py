# modules/CommunicationHub.py
import ray

@ray.remote
class CommunicationHub:
    """Facilitates real-time communication between nodes."""
    def __init__(self):
        self.messages = []

    def broadcast(self, message):
        """Broadcast a message to all nodes."""
        self.messages.append(message)
        return f"Message broadcasted: {message}"

    def get_messages(self):
        """Retrieve all messages."""
        return self.messages

    def clear_messages(self):
        """Clear all stored messages."""
        self.messages = []
        return "Messages cleared."
