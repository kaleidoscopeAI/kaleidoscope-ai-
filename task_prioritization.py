node_management/optimization/task_prioritization.py
Python

class TaskPrioritizer:
    def __init__(self, node_manager: NodeLifeCycleManager):
        self.node_manager = node_manager

    def prioritize_tasks(self, tasks: list) -> list:
        """Prioritize tasks based on their priority and required resources."""
        # Sort tasks by priority (higher value means higher priority) and then by required capacity
        return sorted(tasks, key=lambda task: (task.get('priority', 0), -task.get('required_capacity', 0)), reverse=True)

    def update_task_priority(self, task_id: str, new_priority: int):
        """Update the priority of a specific task."""
        for node in self.node_manager.nodes.values():
            for task in node.tasks:
                if task['task_id'] == task_id:
                    task['priority'] = new_priority
                    return

    def get_prioritized_tasks(self, node_id: str = None) -> list:
        """Get a list of tasks prioritized, optionally for a specific node."""
        if node_id:
            node = self.node_manager.get_node(node_id)
            if node:
                return self.prioritize_tasks(node.tasks)
            else:
                return []
        else:
            all_tasks = []
            for node in self.node_manager.nodes.values():
                all_tasks.extend(node.tasks)
            return self.prioritize_tasks(all_tasks)
        
    def get_state(self) -> dict:
      """Return the current state of the task prioritizer."""
      return {
          'prioritized_tasks': self.get_prioritized_tasks()
      }
