# /visualization/VisualizationTools.py

import matplotlib.pyplot as plt
import networkx as nx
import time

class VisualizationTools:
    def __init__(self, num_iterations):
        self.performance_history = []
        self.uncertainty_history = []
        self.num_iterations = num_iterations
        self.iteration_times = []

        # Pre-allocate the figure and axes for the live plots
        plt.ion()  # Turn on interactive mode
        self.fig, self.axs = plt.subplots(2, 2, figsize=(18, 10))
        plt.tight_layout(pad=4.0)

        # Customize the plots
        self.axs[0, 0].set_title("Performance Over Iterations")
        self.axs[0, 0].set_xlabel("Iteration")
        self.axs[0, 0].set_ylabel("Performance Metric")

        self.axs[0, 1].set_title("Uncertainty Distribution (Current Iteration)")
        self.axs[0, 1].set_xlabel("Uncertainty")
        self.axs[0, 1].set_ylabel("Frequency")

        self.axs[1, 0].set_title("Resonance Network")
        self.axs[1, 0].set_xlabel("Node Position X")  # Assuming a 2D layout for nodes
        self.axs[1, 0].set_ylabel("Node Position Y")

        self.axs[1, 1].set_title("Iteration Time")
        self.axs[1, 1].set_xlabel("Iteration")
        self.axs[1, 1].set_ylabel("Time (seconds)")

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update_performance(self, performance_metric):
        self.performance_history.append(performance_metric)
        self.axs[0, 0].clear()
        self.axs[0, 0].plot(self.performance_history, marker='o', linestyle='-', color='blue')
        self.axs[0, 0].set_title("Performance Over Iterations")
        self.axs[0, 0].set_xlabel("Iteration")
        self.axs[0, 0].set_ylabel("Performance Metric")
        self.axs[0, 0].set_xlim([0, self.num_iterations])
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update_uncertainty(self, uncertainties):
        self.uncertainty_history.append(uncertainties)
        self.axs[0, 1].clear()
        self.axs[0, 1].hist(uncertainties, bins='auto', alpha=0.7, color='green', edgecolor='black')
        self.axs[0, 1].set_title("Uncertainty Distribution (Current Iteration)")
        self.axs[0, 1].set_xlabel("Uncertainty")
        self.axs[0, 1].set_ylabel("Frequency")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update_resonance_network(self, resonance_network):
        self.axs[1, 0].clear()
        pos = nx.spring_layout(resonance_network, seed=42)
        nx.draw(resonance_network, pos, with_labels=True, node_color='skyblue', node_size=1500, edge_color='gray',
                linewidths=1, font_size=10, font_weight='bold', alpha=0.9, ax=self.axs[1, 0])
        self.axs[1, 0].set_title("Resonance Network")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update_iteration_times(self, iteration_time):
        self.iteration_times.append(iteration_time)
        self.axs[1, 1].clear()
        self.axs[1, 1].plot(self.iteration_times, marker='o', linestyle='-', color='purple')
        self.axs[1, 1].set_title("Iteration Time")
        self.axs[1, 1].set_xlabel("Iteration")
        self.axs[1, 1].set_ylabel("Time (seconds)")
        self.axs[1, 1].set_xlim([0, self.num_iterations])
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def finalize_plots(self):
        plt.ioff()  # Turn off interactive mode
        plt.show()
