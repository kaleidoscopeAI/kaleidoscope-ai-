node_management/optimization/resource_allocation.py
Python

class ResourceAllocator:
    def __init__(self, node_manager: NodeLifeCycleManager):
        self.node_manager = node_manager

    def allocate_resources(self, task: dict) -> str:
        """Allocate resources for a given task based on node availability and capacity."""
        eligible_nodes = self._find_eligible_nodes(task)
        if eligible_nodes:
            chosen_node = self._choose_node(eligible_nodes)
            chosen_node.assign_task(task)
            return chosen_node.node_id
        else:
            print(f"No eligible node found for task: {task['task_id']}")
            return None

    def _find_eligible_nodes(self,
 task: dict) -> list:
        """Find nodes that are eligible to execute a given task."""
        eligible_nodes = []
        for node in self.node_manager.nodes.values():
            if node.status == "idle" and node.role == task["required_role"]:
                # Check if node has enough capacity
                if self._calculate_available_capacity(node) >= task.get("required_capacity", 0):
                    eligible_nodes.append(node)
        return eligible_nodes

    def _calculate_available_capacity(self, node: Node) -> float:
        """Calculate the available capacity of a node."""
        used_capacity = len(node.tasks)  # Simplistic: each task uses 1 unit of capacity
        return node.capacity - used_capacity

    def _choose_node(self, eligible_nodes: list) -> Node:
        """Choose a node from the list of eligible nodes based on a specific strategy."""
        # Strategy: Choose the node with the most available capacity
        return max(eligible_nodes, key=lambda node: self._calculate_available_capacity(node))

    def reallocate_resources(self):
        """Reallocate resources across all nodes to optimize performance and energy usage."""
        # Example: Move tasks from overloaded nodes to underloaded nodes
        overloaded_nodes = [node for node in self.node_manager.nodes.values() if self._is_overloaded(node)]
        underloaded_nodes = [node for node in self.node_manager.nodes.values() if self._is_underloaded(node)]

        for overloaded_node in overloaded_nodes:
            while self._is_overloaded(overloaded_node) and underloaded_nodes:
                task_to_move = overloaded_node.tasks.pop()  # Remove task from overloaded node
                target_node = underloaded_nodes.pop(0)
                target_node.assign_task(task_to_move)
                print(f"Task {task_to_move['task_id']} moved from {overloaded_node.node_id} to {target_node.node_id}")
                if not self._is_underloaded(target_node):
                    underloaded_nodes.insert(0, target_node)  # Put it back if it's no longer underloaded

    def _is_overloaded(self, node: Node, threshold: float = 0.8) -> bool:
        """Check if a node is overloaded."""
        return self._calculate_available_capacity(node) < (1 - threshold) * node.capacity

    def _is_underloaded(self, node: Node, threshold: float = 0.5) -> bool:
        """Check if a node is underloaded."""
        return self._calculate_available_capacity(node) > threshold * node.capacity
    
    def get_state(self) -> dict:
      """Return the current state of the resource allocator."""
      return {
          'node_loads': {node_id: {'capacity': node.capacity, 'available_capacity': self._calculate_available_capacity(node)} for node_id, node in self.node_manager.nodes.items()}
      }
