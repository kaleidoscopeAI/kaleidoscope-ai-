node_management/core/task_distribution.py
Python

import random

class TaskDistributor:
    def __init__(self, node_manager: NodeLifeCycleManager):
        self.node_manager = node_manager

    def distribute_tasks(self, tasks: list):
        """Distribute tasks among available nodes based on their roles and capacity."""
        for task in tasks:
            eligible_nodes = self._find_eligible_nodes(task)
            if eligible_nodes:
                chosen_node = self._choose_node(eligible_nodes)
                chosen_node.assign_task(task)
            else:
                print(f"No eligible node found for task: {task['task_id']}")

    def _find_eligible_nodes(self, task: dict) -> list:
        """Find nodes that are eligible to execute a given task."""
        eligible_nodes = []
        for node in self.node_manager.nodes.values():
            if node.status == "idle" and node.role == task["required_role"]:
                load = len(node.tasks) / node.capacity if node.capacity > 0 else 0
                if load < 0.8:  # Consider nodes below 80% load
                  eligible_nodes.append(node)
        return eligible_nodes

    def _choose_node(self, eligible_nodes: list) -> Node:
        """Choose a node from the list of eligible nodes."""
        # Simple strategy: choose the node with the least load
        return min(eligible_nodes, key=lambda node: len(node.tasks))
    
    def rebalance_tasks(self):
      """
      Rebalance tasks across nodes to ensure even distribution and optimal performance.
      """
      # Calculate the average load across nodes
      total_load = sum(len(node.tasks) for node in self.node_manager.nodes.values())
      num_nodes = len(self.node_manager.nodes)
      average_load = total_load / num_nodes if num_nodes > 0 else 0

      underloaded_nodes = []
      overloaded_nodes = []

      for node in self.node_manager.nodes.values():
          if len(node.tasks) < average_load * 0.8:  # 20% below average
              underloaded_nodes.append(node)
          elif len(node.tasks) > average_load * 1.2:  # 20% above average
              overloaded_nodes.append(node)

      # Redistribute tasks from overloaded to underloaded nodes
      for overloaded_node in overloaded_nodes:
          while len(overloaded_node.tasks) > average_load and underloaded_nodes:
              task = overloaded_node.tasks.pop()
              target_node = underloaded_nodes.pop(0)
              target_node.assign_task(task)
              print(f"Task {task['task_id']} reassigned from node {overloaded_node.node_id} to node {target_node.node_id}")

              # Check if the target node is no longer underloaded
              if len(target_node.tasks) >= average_load * 0.8:
                  # If not, put it back in the list for potential reuse
                  underloaded_nodes.insert(0, target_node)
                  
    def get_state(self) -> dict:
        """Returns the current state of the task distributor."""
        return {
            'nodes': {node_id: {'tasks': node.tasks, 'load': len(node.tasks) / node.capacity if node.capacity > 0 else 0} for node_id, node in self.node_manager.nodes.items()}
        }
