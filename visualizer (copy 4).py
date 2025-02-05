# Visualizer module
import networkx as nx
import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self, engine):
        self.engine = engine

    def visualize_gears(self):
        graph = nx.Graph()
        for idx, bank in enumerate(self.engine.memory_banks):
            graph.add_node(idx, memory=len(bank))
        nx.draw(graph, with_labels=True)
        plt.show()

    def visualize_memory(self):
        bank_sizes = [len(bank) for bank in self.engine.memory_banks]
        plt.bar(range(len(bank_sizes)), bank_sizes, color="blue")
        plt.xlabel("Gear ID")
        plt.ylabel("Memory Size")
        plt.title("Memory Distribution Across Gears")
        plt.show()
