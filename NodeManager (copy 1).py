
import ray
from core.Node import Node

@ray.remote
class NodeManager:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node_id, task, datasets):
        if node_id in self.nodes:
            return f"Node {node_id} already exists."
        node = Node.remote(node_id, task, datasets)
        self.nodes[node_id] = node
        return node_id

    def distribute_work(self):
        results = []
        for node_id, node in self.nodes.items():
            result = ray.get(node.explore_data.remote())
            results.append({node_id: result})
        return results

    def shutdown(self):
        for node_id, node in self.nodes.items():
            ray.kill(node)
        self.nodes.clear()
        return "All nodes shut down."
