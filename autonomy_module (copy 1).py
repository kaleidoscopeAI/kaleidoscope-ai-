# Autonomy Module for Node Self-Replication
class AutonomyModule:
    def __init__(self, nodes, replication_threshold):
        self.nodes = nodes
        self.replication_threshold = replication_threshold

    def check_and_replicate(self):
        for node in self.nodes:
            if node.memory_usage() >= self.replication_threshold:
                new_node = node.replicate()
                self.nodes.append(new_node)
                print(f"Node {node.node_id} replicated into Node {new_node.node_id}")
