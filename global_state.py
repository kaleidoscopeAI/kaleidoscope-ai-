from typing import Dict, List, Any
from module_caller import ModuleCaller
from module_receiver import ModuleReceiver

class GlobalState:
    """
    Centralized module for managing system-wide states and coordination.
    Maintains node statuses, task distributions, and global metrics.
    """

    def __init__(self):
        self.module_caller = ModuleCaller()
        self.resource_manager = self.module_caller.resolve("resource_manager.ResourceManager")
        self.task_manager = self.module_caller.resolve("task_manager.TaskManager")
        self.node_states: Dict[str, Dict[str, Any]] = {}  # Tracks individual node states
        self.global_metrics = {
            "total_energy": 0.0,
            "active_nodes": 0,
            "task_count": 0,
        }

    def register_node(self, node_id: str, initial_energy: float):
        """
        Registers a new node with initial energy and tracks its state.
        :param node_id: Unique identifier for the node.
        :param initial_energy: The starting energy for the node.
        """
        try:
            self.resource_manager.register_node(node_id, initial_energy)
            self.node_states[node_id] = {
                "energy": initial_energy,
                "tasks": [],
                "health": 1.0,
            }
            self.update_global_metrics()
        except ModuleNotFoundError as e:
            print("Critical error: Module not found. Ensure 'resource_manager' and 'task_manager' are present.")
            raise e
        except Exception as e:
            print(f"Error registering node {node_id}: {e}")

    def update_node_state(self, node_id: str, energy: float, health: float):
        """
        Updates the state of a specific node.
        :param node_id: The ID of the node to update.
        :param energy: Updated energy level.
        :param health: Updated health level.
        """
        if node_id in self.node_states:
            self.node_states[node_id].update({"energy": energy, "health": health})
            self.update_global_metrics()
        else:
            print(f"Node {node_id} not found in global state.")

    def assign_task(self, task: Dict[str, Any], priority: float) -> bool:
        """
        Assigns a task to the task manager and distributes it to a node.
        :param task: The task data.
        :param priority: The priority of the task.
        :return: True if the task was successfully assigned, False otherwise.
        """
        try:
            task_id = self.task_manager.add_task(task, priority)
            self.global_metrics["task_count"] += 1
            return True
        except Exception as e:
            print(f"Error assigning task: {e}")
            return False

    def handle_node_failure(self, node_id: str):
        """
        Handles the failure of a specific node by redistributing its tasks.
        :param node_id: The ID of the failing node.
        """
        if node_id in self.node_states:
            failed_tasks = self.node_states[node_id]["tasks"]
            for task in failed_tasks:
                self.task_manager.add_task(task, priority=1.0)  # Reassign with high priority
            del self.node_states[node_id]
            self.resource_manager.remove_node(node_id)
            print(f"Node {node_id} has been removed due to failure.")
            self.update_global_metrics()
        else:
            print(f"Node {node_id} not found during failure handling.")

    def balance_resources(self):
        """
        Balances resources across all nodes.
        """
        try:
            self.resource_manager.balance_energy()
            for node_id, energy in self.resource_manager.nodes.items():
                if node_id in self.node_states:
                    self.node_states[node_id]["energy"] = energy
            self.update_global_metrics()
        except Exception as e:
            print(f"Error balancing resources: {e}")

    def update_global_metrics(self):
        """
        Recalculates global metrics based on current node states and tasks.
        """
        try:
            total_energy = sum(node["energy"] for node in self.node_states.values())
            active_nodes = len(self.node_states)
            task_count = len(self.task_manager.task_queue)

            self.global_metrics.update({
                "total_energy": total_energy,
                "active_nodes": active_nodes,
                "task_count": task_count,
            })
        except Exception as e:
            print(f"Error updating global metrics: {e}")

    def get_system_snapshot(self) -> Dict[str, Any]:
        """
        Provides a snapshot of the global system state.
        :return: A dictionary containing global metrics and node states.
        """
        try:
            return {
                "global_metrics": self.global_metrics,
                "node_states": self.node_states,
            }
        except Exception as e:
            print(f"Error generating system snapshot: {e}")
            return {}

# Example usage
if __name__ == "__main__":
    global_state = GlobalState()

    # Register nodes
    global_state.register_node("node_1", 150.0)
    global_state.register_node("node_2", 200.0)

    print("Initial Global State:", global_state.get_system_snapshot())

    # Assign tasks
    global_state.assign_task({"description": "Analyze data A"}, priority=1.0)
    global_state.assign_task({"description": "Process model B"}, priority=2.0)
    print("After Task Assignment:", global_state.get_system_snapshot())

    # Simulate node failure
    global_state.handle_node_failure("node_1")
    print("After Node Failure:", global_state.get_system_snapshot())

    # Balance resources
    global_state.balance_resources()
    print("After Resource Balancing:", global_state.get_system_snapshot())
