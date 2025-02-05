# File: kaleidoscope_ai_core_with_ui.py

import threading
import time
import matplotlib.pyplot as plt
import logging
import csv

# Configure logging
logging.basicConfig(
    filename="system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Node Class
class Node:
    def __init__(self, node_id, initial_energy=100, initial_knowledge=0):
        self.node_id = node_id
        self.energy = initial_energy
        self.knowledge = initial_knowledge

    def execute_task(self, task_complexity, task_context=None):
        """Executes a task, consuming energy and gaining knowledge."""
        energy_cost = task_complexity * 2
        knowledge_gain = task_complexity * 1.5

        if self.energy >= energy_cost:
            self.energy -= energy_cost
            self.knowledge += knowledge_gain
            return {
                "status": "task_complete",
                "knowledge_gain": knowledge_gain,
                "remaining_energy": self.energy
            }
        else:
            return {
                "status": "task_failed",
                "reason": "Insufficient energy",
                "remaining_energy": self.energy
            }

    def adjust_learning_rate(self, success_rate):
        """Adjusts energy usage or knowledge accumulation based on success rate."""
        if success_rate > 0.8:
            self.energy += 10  # Reward nodes with energy
        elif success_rate < 0.5:
            self.energy -= 5  # Penalize nodes with energy reduction

# Thought Nexus Class
class ThoughtNexus:
    def __init__(self):
        self.global_insights = []
        self.task_queue = []

    def collect_insights(self, node_insights):
        """Aggregates insights from all nodes."""
        self.global_insights.extend(node_insights)
        print(f"Collected Insights: {self.global_insights}")

    def prioritize_tasks(self, tasks, environment):
        """Reorders tasks dynamically based on real-time node performance and generated insights."""
        # Incorporate dynamic prioritization using node performance and global insights
        for task in tasks:
            importance_factor = task.get("context", {}).get("importance", 1)
            task["adjusted_priority"] = task.get("priority", 1) * importance_factor

            # Adjust priority based on energy and knowledge of best node
            best_node = max(environment.nodes, key=lambda n: (n.energy, n.knowledge))
            task["adjusted_priority"] += best_node.energy * 0.01 + best_node.knowledge * 0.02

        # Sort tasks based on dynamically adjusted priorities
        self.task_queue = sorted(tasks, key=lambda x: x["adjusted_priority"], reverse=True)
        print(f"Dynamically Prioritized Task Queue: {self.task_queue}")

    def distribute_tasks(self, environment):
        """Distributes tasks to nodes based on priority and node performance."""
        for task in self.task_queue:
            best_node = max(environment.nodes, key=lambda n: (n.energy, n.knowledge))
            try:
                result = best_node.execute_task(
                    task_complexity=task["complexity"],
                    task_context=task.get("context", {})
                )
                print(f"Task {task['id']} assigned to Node {best_node.node_id} with result: {result}")
                logging.info(f"Task {task['id']} assigned to Node {best_node.node_id} with result: {result}")
            except Exception as e:
                error_message = f"Error assigning Task {task['id']} to Node {best_node.node_id}: {e}"
                print(error_message)
                logging.error(error_message)

    def feedback_loop(self, environment):
        """Analyzes task outcomes and updates node performance."""
        for node in environment.nodes:
            success_rate = len([t for t in self.task_queue if t.get("status") == "task_complete"]) / len(self.task_queue) if self.task_queue else 0
            node.adjust_learning_rate(success_rate)
        print("Feedback loop executed; learning rates adjusted.")
        logging.info("Feedback loop executed; learning rates adjusted.")


# Enhancing the Environment Class
class Environment:
    def __init__(self):
        self.nodes = []
        self.dependencies = {}
        self.data_bank = {}
        self.performance_log = []
        self.is_running = False  # New field to track the system's state
        self.nexus = ThoughtNexus()  # Adding Thought Nexus instance

    def add_node(self, node):
        """Adds a node to the environment."""
        self.nodes.append(node)

    def monitor_performance(self):
        """Monitors real-time performance of nodes and dependencies, logs data for long-term trend analysis."""
        node_performance = [
            {
                "node_id": node.node_id,
                "energy": node.energy,
                "knowledge": node.knowledge
            } for node in self.nodes
        ]

        print("Performance:", node_performance)
        logging.info(f"Performance: {node_performance}")

        # Log performance data to a CSV file for long-term analysis
        with open("performance_data.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                # Write header if the file is empty
                writer.writerow(["Timestamp", "Node ID", "Energy", "Knowledge"])
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            for node in node_performance:
                writer.writerow([timestamp, node["node_id"], node["energy"], node["knowledge"]])

    def process_nexus_tasks(self):
        """Allows the Thought Nexus to distribute tasks and collect feedback."""
        try:
            self.nexus.distribute_tasks(self)
            self.nexus.feedback_loop(self)
        except Exception as e:
            error_message = f"Error during Nexus task processing: {e}"
            print(error_message)
            logging.error(error_message)

    def visualize_state(self, state):
        """Visualizes the system's current state in real-time."""
        state_map = {
            'play': 'System Running',
            'pause': 'System Paused',
            'stop': 'System Stopped'
        }
        plt.figure(figsize=(5, 5))
        plt.text(0.5, 0.5, state_map.get(state, 'Unknown State'),
                 horizontalalignment='center', verticalalignment='center',
                 fontsize=20, color='blue')
        plt.title('System State Visualization')
        plt.axis('off')
        plt.show()


# Play, Pause, Stop, and Inject Functions
def play_system(environment):
    """Starts the system's operations."""
    print("System started.")
    logging.info("System started.")
    environment.visualize_state('play')
    environment.is_running = True

    while environment.is_running:
        environment.monitor_performance()
        environment.process_nexus_tasks()
        time.sleep(1)  # Simulates periodic system operations

    print("System stopped.")
    logging.info("System stopped.")


def pause_system(environment):
    """Pauses the system's operations."""
    print("System paused.")
    logging.info("System paused.")
    environment.visualize_state('pause')
    environment.is_running = False


def stop_system(environment):
    """Stops the system completely."""
    environment.is_running = False
    print("System terminated.")
    logging.info("System terminated.")
    environment.visualize_state('stop')


def inject_task(environment, node_id, task):
    """Injects a task directly into a specified node and logs the action."""
    for node in environment.nodes:
        if node.node_id == node_id:
            try:
                result = node.execute_task(
                    task_complexity=task['complexity'],
                    task_context=task.get('context', {})
                )
                print(f"Task injected to Node {node_id}: {result}")
                logging.info(f"Task {task['id']} injected to Node {node_id}: {result}")
            except Exception as e:
                error_message = f"Error injecting Task {task['id']} to Node {node_id}: {e}"
                print(error_message)
                logging.error(error_message)
            return

    error_message = f"Node {node_id} not found in the environment."
    print(error_message)
   
