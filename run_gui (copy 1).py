
import tkinter as tk
from tkinter import ttk
from threading import Thread
from visualization.interactive_visuals import StunningVisualizer
from core.node import Node

class KaleidoscopeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Kaleidoscope System")

        # Parameter inputs
        ttk.Label(root, text="Number of Nodes:").grid(row=0, column=0, padx=10, pady=5, sticky="W")
        self.num_nodes = ttk.Entry(root)
        self.num_nodes.grid(row=0, column=1, padx=10, pady=5)
        self.num_nodes.insert(0, "10")

        ttk.Label(root, text="Simulation Steps:").grid(row=1, column=0, padx=10, pady=5, sticky="W")
        self.steps = ttk.Entry(root)
        self.steps.grid(row=1, column=1, padx=10, pady=5)
        self.steps.insert(0, "50")

        # Start Simulation Button
        self.start_button = ttk.Button(root, text="Start Simulation", command=self.start_simulation)
        self.start_button.grid(row=2, column=0, columnspan=2, pady=20)

        # Status Label
        self.status_label = ttk.Label(root, text="Ready")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=10)

    def start_simulation(self):
        """Start the simulation in a separate thread."""
        try:
            num_nodes = int(self.num_nodes.get())
            steps = int(self.steps.get())
            self.status_label.config(text="Running Simulation...")
            Thread(target=self.run_simulation, args=(num_nodes, steps), daemon=True).start()
        except ValueError:
            self.status_label.config(text="Invalid Input. Please enter valid numbers.")

    def run_simulation(self, num_nodes, steps):
        """Run the simulation and display visualization."""
        nodes = [Node(node_id=f"Node_{i}") for i in range(num_nodes)]
        visualizer = StunningVisualizer(nodes)

        for step in range(steps):
            for node in nodes:
                node.move()
                if node.energy <= 0:
                    nodes.remove(node)

        self.status_label.config(text="Simulation Complete")
        visualizer.run()

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = KaleidoscopeApp(root)
    root.mainloop()
        