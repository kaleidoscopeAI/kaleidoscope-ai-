from typing import List, Dict, Any, Callable

class KaleidoscopeEngine:
    """
    Central processing engine for Kaleidoscope AI, responsible for managing
    multi-modal data processing, task distribution, and advanced pattern recognition.
    """

    def __init__(self):
        self.nodes = []  # List of active NodeCore instances
        self.global_task_queue = []  # Centralized task queue
        self.pattern_registry = []  # Repository for recognized patterns
        self.error_logs = []  # Error logging system
        self.system_health = {"active_nodes": 0, "task_completion_rate": 0.0, "average_energy": 0.0}

    def register_node(self, node):
        """
        Registers a new node with the engine.
        :param node: A NodeCore instance to be registered.
        """
        self.nodes.append(node)
        print(f"Node {node.node_id} registered with KaleidoscopeEngine.")
        self.update_system_health()

    def distribute_tasks(self):
        """
        Distributes tasks from the global task queue to registered nodes based on their availability.
        Logs tasks that cannot be assigned due to insufficient resources.
        """
        # Sort tasks by priority before distribution
        self.global_task_queue.sort(key=lambda x: x.get("priority", 1), reverse=True)

        for task in self.global_task_queue:
            assigned = False
            for node in self.nodes:
                if node.current_energy >= task.get("energy_required", 0.1):
                    node.assign_task(task)
                    print(f"Task {task['id']} assigned to Node {node.node_id}.")
                    assigned = True
                    break
            if not assigned:
                self.error_logs.append(f"Task {task['id']} could not be assigned due to insufficient resources.")

        # Clear the global task queue after distribution
        self.global_task_queue.clear()
        self.update_system_health()

    def retry_failed_tasks(self):
        """
        Retries tasks that failed to be reassigned, prioritizing high-priority tasks.
        Includes logic to dynamically adjust task retries based on system metrics.
        """
        print("Retrying failed tasks...")
        failed_tasks = [task for task in self.global_task_queue if task.get("retries", 0) < 3]
        for task in failed_tasks:
            task["retries"] = task.get("retries", 0) + 1
            print(f"Retrying task {task['id']} (Attempt {task['retries']}).")
            self.add_task_to_queue(task)
        self.global_task_queue = [task for task in self.global_task_queue if task.get("retries", 0) < 3]

    def process_data(self, data: List[Dict[str, Any]], processing_fn: Callable[[Dict[str, Any]], Any]):
        """
        Processes incoming data using a custom processing function and stores results in the pattern registry.
        Supports advanced pattern recognition logic with contextual prioritization.
        :param data: A list of data points to be processed.
        :param processing_fn: A function that processes a data point and returns a result.
        """
        for item in data:
            try:
                result = processing_fn(item)
                self.pattern_registry.append(result)
                print(f"Processed data: {item}, Result: {result}")
            except Exception as e:
                self.error_logs.append(f"Error processing data {item['id']}: {str(e)}")

    def integrate_learning_feedback(self):
        """
        Leverages insights from LearningCore to dynamically optimize task distribution and processing.
        """
        print("Integrating feedback from LearningCore...")
        for node in self.nodes:
            learning_data = node.learning_core.summarize()
            print(f"Node {node.node_id} Learning Data: {learning_data}")
            for task in self.global_task_queue:
                if task["id"] in learning_data:
                    task["priority"] += learning_data[task["id"]].get("weight", 0)
        self.global_task_queue.sort(key=lambda x: x.get("priority", 1), reverse=True)

    def analyze_patterns(self):
        """
        Analyzes patterns stored in the pattern registry to derive actionable insights.
        """
        if not self.pattern_registry:
            print("No patterns to analyze.")
            return

        print("Analyzing patterns...")
        for pattern in self.pattern_registry:
            print(f"Pattern: {pattern}")

    def export_state(self, filename: str):
        """
        Exports the current state of the engine to a file for external analysis.
        :param filename: Name of the file to export the state.
        """
        state = self.summarize_engine_state()
        try:
            with open(filename, "w") as file:
                file.write(str(state))
            print(f"Engine state exported to {filename}.")
        except Exception as e:
            print(f"Failed to export engine state: {str(e)}")

    def summarize_engine_state(self):
        """
        Summarizes the current state of the engine, including node states and patterns.
        Includes insights from LearningCore.
        :return: A dictionary summarizing the engine's state.
        """
        learning_feedback = {
            node.node_id: node.learning_core.summarize()
            for node in self.nodes
        }
        return {
            "total_nodes": len(self.nodes),
            "registered_nodes": [node.node_id for node in self.nodes],
            "total_patterns": len(self.pattern_registry),
            "pending_tasks": len(self.global_task_queue),
            "system_health": self.system_health,
            "error_logs": len(self.error_logs),
            "learning_feedback": learning_feedback,
        }

    def add_task_to_queue(self, task: Dict[str, Any]):
        """
        Adds a task to the global task queue.
        :param task: A dictionary representing the task details.
        """
        self.global_task_queue.append(task)
        print(f"Task {task['id']} added to the global queue.")

    def update_system_health(self):
        """
        Updates the system health metrics based on current node states and task activity.
        Utilizes advanced metrics for more granular system insights.
        """
        if not self.nodes:
            self.system_health = {"active_nodes": 0, "task_completion_rate": 0.0, "average_energy": 0.0}
            return

        active_nodes = len(self.nodes)
        total_energy = sum(node.current_energy for node in self.nodes)
        total_capacity = sum(node.energy_capacity for node in self.nodes)
        patterns_processed = len(self.pattern_registry)
        pending_tasks = len(self.global_task_queue)

        self.system_health = {
            "active_nodes": active_nodes,
            "task_completion_rate": patterns_processed / (patterns_processed + pending_tasks + 1),
            "average_energy": total_energy / total_capacity,
        }
        print(f"System health updated: {self.system_health}")

    def visualize_state(self):
        """
        Placeholder for visualization integration.
        """
        print("Visualizing system state...")
        print(self.summarize_engine_state())
