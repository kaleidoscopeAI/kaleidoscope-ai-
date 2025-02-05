
import json
import os

class MemoryGraph:
    def __init__(self, memory_file="Unified_AI_Core/data/GlobalMemory.json"):
        self.memory_file = memory_file
        self.graph = {}

    def load_memory(self):
        """Load memory graph from a file."""
        try:
            with open(self.memory_file, "r") as file:
                self.graph = json.load(file)
                print(f"Memory graph loaded with {len(self.graph)} nodes.")
        except FileNotFoundError:
            print("Memory file not found. Starting with an empty graph.")
            self.graph = {}

    def save_memory(self, batch_mode=False):
        """Save memory graph to a file."""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        if batch_mode:
            print("Batch save in progress...")
        with open(self.memory_file, "w") as file:
            json.dump(self.graph, file, indent=4)
        if batch_mode:
            print("Batch save complete.")
        else:
            print("Memory graph saved.")

    def add_relationship(self, node_a, node_b, relationship_type, verbose=True):
        """Add a relationship between two nodes in the memory graph."""
        if node_a not in self.graph:
            self.graph[node_a] = {}
        self.graph[node_a][node_b] = relationship_type
        if verbose:
            print(f"Added relationship: {node_a} -> {node_b} ({relationship_type})")

    def query_relationships(self, node):
        """Query all relationships for a given node."""
        return self.graph.get(node, {})

# Example usage of MemoryGraph
if __name__ == "__main__":
    memory_graph = MemoryGraph()
    memory_graph.load_memory()
    memory_graph.add_relationship("Node1", "Node2", "supports", verbose=True)
    memory_graph.add_relationship("Node2", "Node3", "connected", verbose=True)
    print("Node1 Relationships:", memory_graph.query_relationships("Node1"))
    memory_graph.save_memory(batch_mode=True)
