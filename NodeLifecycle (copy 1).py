
import random
import copy

class Node:
    def __init__(self, name, attributes=None):
        self.name = name
        self.attributes = attributes or {}
        self.children = []  # Track replicated nodes

    def replicate(self):
        """Replicate the node with inherited and slightly modified attributes."""
        new_name = f"{self.name}_child_{random.randint(1000, 9999)}"
        # Modify attributes slightly for evolution
        new_attributes = copy.deepcopy(self.attributes)
        for key in new_attributes:
            if isinstance(new_attributes[key], (int, float)):
                new_attributes[key] += random.uniform(-0.1, 0.1)  # Small random change

        child_node = Node(new_name, new_attributes)
        self.children.append(child_node)
        print(f"Node {self.name} replicated into {child_node.name}.")
        return child_node

    def specialize(self, specialization_key, specialization_value):
        """Specialize the node by adding a unique attribute."""
        self.attributes[specialization_key] = specialization_value
        print(f"Node {self.name} specialized with {specialization_key}: {specialization_value}.")

# Example usage of Node lifecycle
if __name__ == "__main__":
    parent_node = Node("ParentNode", {"energy": 100, "task": "data_processing"})
    print(f"Parent Node: {parent_node.name}, Attributes: {parent_node.attributes}")

    # Replicate and specialize
    child_node = parent_node.replicate()
    child_node.specialize("environment", "healthcare")

    print(f"Child Node: {child_node.name}, Attributes: {child_node.attributes}")
