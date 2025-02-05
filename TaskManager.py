# Kaleidoscope AI: Task Manager Module
# File: /integration/TaskManager.py

import heapq
import time
from typing import Dict, List, Any

class Task:
    def __init__(self, task_id: str, priority: int, resource_demand: float, data: Dict):
        self.task_id = task_id
        self.priority = priority
        self.resource_demand = resource_demand
        self.data = data
        self.timestamp = time.time()

    def __lt__(self, other):
        return self.priority > other.priority or (self.priority == other.priority and self.timestamp < other.timestamp)

class TaskManager:
    """Manages tasks, prioritization, and resource allocation."""
    def __init__(self):
        self.task_queue: List[Task] = []
        self.active_tasks: Dict[str, Task] = {}

    def add_task(self, task_id: str, priority: int, resource_demand: float, data: Dict):
        """Add a new task to the queue."""
        task = Task(task_id, priority, resource_demand, data)
        heapq.heappush(self.task_queue, task)
        print(f"Task {task_id} added with priority {priority} and resource demand {resource_demand}.")

    def assign_task(self, available_resources: float) -> Any:
        """Assign the highest priority task that fits within available resources."""
        while self.task_queue:
            task = heapq.heappop(self.task_queue)
            if task.resource_demand <= available_resources:
                self.active_tasks[task.task_id] = task
                print(f"Task {task.task_id} assigned with priority {task.priority}.")
                return task
            else:
                print(f"Task {task.task_id} requires {task.resource_demand} resources, skipping.")
                heapq.heappush(self.task_queue, task)  # Reinsert if not assignable
                break
        print("No suitable tasks for the current resource availability.")
        return None

    def complete_task(self, task_id: str):
        """Mark a task as complete and remove it from active tasks."""
        if task_id in self.active_tasks:
            completed_task = self.active_tasks.pop(task_id)
            print(f"Task {task_id} completed.")
            return completed_task
        print(f"Task {task_id} not found in active tasks.")
        return None

    def reassign_task(self, task_id: str, available_resources: float):
        """Attempt to reassign a task if its conditions have changed."""
        if task_id in self.active_tasks:
            task = self.active_tasks.pop(task_id)
            print(f"Reassigning Task {task_id}...")
            self.add_task(task.task_id, task.priority, task.resource_demand, task.data)
            return self.assign_task(available_resources)
        print(f"Task {task_id} not found for reassignment.")
        return None

    def display_queue(self):
        """Display the current state of the task queue."""
        print("Task Queue:")
        for task in sorted(self.task_queue, reverse=True):
            print(f"Task ID: {task.task_id}, Priority: {task.priority}, Resources: {task.resource_demand}")

    def display_active_tasks(self):
        """Display the current active tasks."""
        print("Active Tasks:")
        for task_id, task in self.active_tasks.items():
            print(f"Task ID: {task_id}, Priority: {task.priority}, Resources: {task.resource_demand}")

# Example Usage
if __name__ == "__main__":
    manager = TaskManager()

    # Adding tasks
    manager.add_task("task1", priority=5, resource_demand=3.0, data={"info": "Analyze dataset A"})
    manager.add_task("task2", priority=8, resource_demand=1.5, data={"info": "Generate report B"})
    manager.add_task("task3", priority=2, resource_demand=4.0, data={"info": "Run simulation C"})

    # Assign tasks with available resources
    manager.assign_task(available_resources=2.0)
    manager.assign_task(available_resources=5.0)

    # Complete a task
    manager.complete_task("task2")

    # Reassign a task
    manager.reassign_task("task1", available_resources=4.0)

    # Display current queue and active tasks
    manager.display_queue()
    manager.display_active_tasks()
