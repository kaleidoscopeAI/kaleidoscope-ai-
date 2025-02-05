from typing import List, Dict, Any, Callable
import numpy as np

class LearningCore:
    """
    Simulated LearningCore for managing adaptive learning and knowledge integration.
    """
    def __init__(self):
        self.knowledge_base = {}
        self.learning_rate = 0.1

    def learn(self, data: List[Dict[str, Any]], contribution_fn: Callable[[Dict[str, Any], float], float]) -> float:
        knowledge_gain = 0.0
        for entry in data:
            contribution = contribution_fn(entry, self.learning_rate)
            self.knowledge_base[entry['id']] = contribution
            knowledge_gain += contribution
        return knowledge_gain

    def summarize(self) -> Dict[str, Any]:
        return {
            "total_knowledge": len(self.knowledge_base),
            "learning_rate": self.learning_rate,
        }

class NodeCore:
    """
    Core module responsible for managing node traits, replication, task execution,
    and integration with the LearningCore for adaptive improvements.
    Designed for seamless integration with Kaleidoscope AI's modular architecture.
    """

    def __init__(self, node_id: str, traits: Dict[str, float], energy_capacity: float):
        self.node_id = node_id
        self.traits = traits
        self.energy_capacity = energy_capacity
        self.current_energy = energy_capacity
        self.task_queue = []  # Stores tasks assigned to the node
        self.replication_threshold = traits.get("replication_threshold", 0.8)
        self.energy_efficiency = traits.get("energy_efficiency", 1.0)
        self.learning_core = LearningCore()  # Integrated LearningCore
        self.collaboration_nodes = []  # Nodes this node collaborates with
        self.completed_tasks = []  # Historical task tracking

    def assign_task(self, task: Dict[str, Any]):
        """
        Assigns a task to the node's task queue.
        :param task: A dictionary containing task details.
        """
        self.task_queue.append(task)

    def execute_tasks(self):
        """
        Executes tasks in the queue while managing energy usage and task completion.
        Also learns from completed tasks using the integrated LearningCore.
        Shares task insights with collaboration nodes for distributed learning.
        """
        task_data = []

        for task in self.task_queue:
            energy_required = task.get("energy_required", 0.1)

            if self.current_energy >= energy_required:
                self.current_energy -= energy_required / self.energy_efficiency
                self.completed_tasks.append(task)
                task_data.append({"id": task["id"], "value": energy_required})
            else:
                print(f"Node {self.node_id}: Insufficient energy for task {task['id']}.")

        self.task_queue = [task for task in self.task_queue if task not in self.completed_tasks]

        # Use LearningCore to learn from completed tasks
        if task_data:
            contribution_fn = lambda entry, rate: entry["value"] * rate
            knowledge_gain = self.learning_core.learn(task_data, contribution_fn)
            print(f"Node {self.node_id}: Learned {knowledge_gain} from completed tasks.")

        # Share insights with collaboration nodes
        for node in self.collaboration_nodes:
            node.receive_shared_knowledge(task_data)

        return self.completed_tasks

    def prioritize_tasks(self):
        """
        Reorders the task queue based on energy requirements and importance.
        """
        self.task_queue.sort(key=lambda x: (x.get("priority", 1), x.get("energy_required", 0.1)))
        print(f"Node {self.node_id}: Task queue reprioritized.")

    def redistribute_energy(self):
        """
        Shares excess energy with collaboration nodes needing support.
        """
        for node in self.collaboration_nodes:
            if node.current_energy / node.energy_capacity < 0.5 and self.current_energy / self.energy_capacity > 0.7:
                energy_shared = 0.1 * self.energy_capacity
                self.current_energy -= energy_shared
                node.recharge(energy_shared)
                print(f"Node {self.node_id}: Shared {energy_shared} energy with {node.node_id}.")

    def replicate(self):
        """
        Determines if the node should replicate based on energy and traits.
        :return: A new NodeCore instance if replication is successful, otherwise None.
        """
        if self.current_energy / self.energy_capacity >= self.replication_threshold:
            new_traits = {
                trait: value * (1 + 0.1 * (0.5 - value))  # Slight variation to traits
                for trait, value in self.traits.items()
            }
            new_node = NodeCore(f"{self.node_id}_child", new_traits, self.energy_capacity)
            self.current_energy /= 2  # Energy is split between parent and child
            print(f"Node {self.node_id}: Replication successful, created {new_node.node_id}.")

            # Share learned knowledge with the new node
            new_node.learning_core.knowledge_base = self.learning_core.knowledge_base.copy()
            print(f"Node {new_node.node_id}: Inherited knowledge from {self.node_id}.")

            return new_node
        else:
            print(f"Node {self.node_id}: Insufficient energy for replication.")
        return None

    def recharge(self, energy_input: float):
        """
        Recharges the node's energy up to its capacity.
        :param energy_input: Amount of energy to recharge.
        """
        self.current_energy = min(self.energy_capacity, self.current_energy + energy_input)
        print(f"Node {self.node_id}: Recharged to {self.current_energy}/{self.energy_capacity}.")

    def receive_shared_knowledge(self, knowledge: List[Dict[str, Any]]):
        """
        Receives shared knowledge from other nodes and integrates it using LearningCore.
        :param knowledge: A list of knowledge entries shared by collaborating nodes.
        """
        contribution_fn = lambda entry, rate: entry["value"] * rate
        knowledge_gain = self.learning_core.learn(knowledge, contribution_fn)
        print(f"Node {self.node_id}: Integrated {knowledge_gain} knowledge from collaborators.")

    def collaborate_with(self, node: 'NodeCore'):
        """
        Establishes collaboration with another node for knowledge sharing.
        :param node: The NodeCore instance to collaborate with.
        """
        if node not in self.collaboration_nodes:
            self.collaboration_nodes.append(node)
            node.collaboration_nodes.append(self)
            print(f"Node {self.node_id}: Collaboration established with {node.node_id}.")

    def summarize(self):
        """
        Summarizes the node's current state.
        :return: A dictionary containing node details.
        """
        return {
            "node_id": self.node_id,
            "traits": self.traits,
            "current_energy": self.current_energy,
            "energy_capacity": self.energy_capacity,
            "task_queue_size": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "learning_core_summary": self.learning_core.summarize(),
            "collaboration_nodes": [node.node_id for node in self.collaboration_nodes],
        }

# Example usage
if __name__ == "__main__":
    # Initialize nodes
    initial_traits = {
        "replication_threshold": 0.8,
        "energy_efficiency": 1.2,
    }
    node_1 = NodeCore("node_1", initial_traits, energy_capacity=10.0)
    node_2 = NodeCore("node_2", initial_traits, energy_capacity=10.0)

    # Establish collaboration
    node_1.collaborate_with(node_2)

    # Assign tasks to node_1
    node_1.assign_task({"id": "task_1", "energy_required": 2.0, "priority": 2})
    node_1.assign_task({"id": "task_2", "energy_required": 5.0, "priority": 1})

    # Prioritize tasks on node_1
    node_1.prioritize_tasks()

    # Execute tasks on node_1
    completed = node_1.execute_tasks()
    print(f"Node_1 Completed Tasks: {completed}")

    # Redistribute energy between nodes
    node_1.redistribute_energy()

    # Recharge node_1
    node_1.recharge(energy_input=5.0)

    # Attempt replication for node_1
    new_node = node_1.replicate()

    # Summarize node states
    print("Node_1 Summary:", node_1.summarize())
    print("Node_2 Summary:", node_2.summarize())
    if new_node:
        print("New Node Summary:", new_node.summarize())
