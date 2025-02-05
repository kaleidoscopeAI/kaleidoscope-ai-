
from core.node import Node
from core.resource_manager import ResourceManager

def simulate_network(steps=5):
    manager = ResourceManager()
    nodes = [Node(i, 1.0) for i in range(5)]
    for step in range(steps):
        manager.allocate(nodes)
        print(f"Step {step}: Node states -> {[node.energy for node in nodes]}")
