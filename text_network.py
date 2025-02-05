# text_network.py

from typing import Dict, List
from core.organic_node import OrganicNode
from learning.text_processing import TextProcessor

class TextNetwork:
    """Manages the growth and interaction of text nodes"""

    def __init__(self):
        self.nodes: Dict[str, OrganicNode] = {}
        self.processor = TextProcessor()

    def add_node(self, node: OrganicNode):
        """Adds a new text node to the network"""
        self.nodes[node.id] = node

    def process_input(self, text: str):
        """Distributes text processing across nodes"""
        results = []
        for node in self.nodes.values():
            if node.energy > 0:
                patterns = self.processor.extract_patterns(text)
                node.process_information(text)
                validation = self.processor.validate_nouns(
                    patterns, node.long_term_memory
                )
                results.append({"node_id": node.id, "validation": validation})
        return results

    def grow_network(self, steps: int = 1):
        """Simulates network growth by replicating nodes"""
        for _ in range(steps):
            for node in list(self.nodes.values()):
                if node.energy > 20 and len(node.long_term_memory) > 10:
                    replicator = NodeReplicator(node)
                    child_node = replicator.replicate()
                    self.add_node(child_node)
