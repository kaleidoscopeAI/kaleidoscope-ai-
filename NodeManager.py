
from modules.PerspectiveManager import PerspectiveManager
from modules.SeedManager import SeedManager
from modules.MirroredNetwork import MirroredNetwork

class NodeManager:
    def __init__(self):
        self.nodes = []  # List to store registered nodes
        self.perspective_manager = PerspectiveManager()
        self.seed_manager = SeedManager()
        self.mirrored_network = MirroredNetwork()

    def load_nodes(self):
        """
        Load initial nodes into the system and initialize networks.
        """
        print("Loading nodes...")
        self.nodes = [
            {"name": "TextProcessor", "status": "active"},
            {"name": "VisualProcessor", "status": "active"},
            {"name": "MemoryGraph", "status": "idle"},
        ]
        self.mirrored_network.initialize_networks(self.nodes)
        print(f"Nodes loaded: {len(self.nodes)} nodes initialized in mirrored networks.")

    def update_nodes(self):
        """
        Update the status of all nodes during each tick.
        """
        print("Updating nodes...")
        for node in self.nodes:
            if node["status"] == "active":
                print(f"Node {node['name']} is processing data...")
                # Example: Process perspectives for active nodes
                if node["name"] == "TextProcessor":
                    data = "Sample text data"
                    self.perspective_manager.process_perspectives(data)
            elif node["status"] == "idle":
                print(f"Node {node['name']} is waiting for tasks.")
        # Synchronize mirrored networks after updates
        self.mirrored_network.sync_networks()

    def register_node(self, name, parameters=None):
        """
        Dynamically register a new node using the seed manager.
        """
        seed = self.seed_manager.generate_seed(name, parameters)
        new_node = self.seed_manager.initialize_from_seed(name)
        self.nodes.append(new_node)
        print(f"Node '{name}' has been registered with parameters: {parameters}.")
