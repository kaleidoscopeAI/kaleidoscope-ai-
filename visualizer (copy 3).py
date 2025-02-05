# Visualizer for System Activities
import matplotlib.pyplot as plt
import networkx as nx

class Visualizer:
    def __init__(self, engine):
        self.engine = engine

    def visualize_gears(self):
        # Visualize memory banks and their current status
        plt.figure(figsize=(10, 5))
        for i, gear in enumerate(self.engine.memory_banks):
            plt.bar(i, len(gear), label=f"Gear {i+1}")
        plt.xlabel("Gears")
        plt.ylabel("Memory Load")
        plt.title("Memory Bank Visualization")
        plt.legend()
        plt.show()

    def visualize_memory(self):
        # Visualize dynamic network activity
        G = nx.DiGraph()
        for idx, gear in enumerate(self.engine.memory_banks):
            G.add_node(f"Gear {idx+1}", size=len(gear))
        nx.draw(G, with_labels=True, node_size=[len(gear) * 100 for gear in self.engine.memory_banks])
        plt.show()
       class Visualizer:
           def visualize_nodes(self, statuses):
        # Display node statuses visually
              for status in statuses:
                
print("Visualizing Node:", status)
