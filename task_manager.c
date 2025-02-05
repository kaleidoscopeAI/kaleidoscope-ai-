#include "task_manager.h"
#include <stdlib.h>
#include <stdio.h>

// Initialize the Task Manager
TaskManager* init_task_manager(uint64_t max_tasks) {
    TaskManager* manager = (TaskManager*)malloc(sizeof(TaskManager));
    if (!manager) return NULL;

    manager->task_queue = (Task*)malloc(sizeof(Task) * max_tasks);
    if (!manager->task_queue) {
        free(manager);
        return NULL;
    }

    manager->max_tasks = max_tasks;
    manager->task_count = 0;

    printf("Task Manager initialized with a capacity of %lu tasks.\n", max_tasks);
    return manager;
}

// Add a Task to the Queue
void add_task(TaskManager* manager, Task* task) {
    if (!manager || manager->task_count >= manager->max_tasks) {
        printf("Task Manager: Cannot add task. Queue is full or manager is uninitialized.\n");
        return;
    }

    manager->task_queue[manager->task_count++] = *task;
    printf("Task %lu added with priority %u.\n", task->task_id, task->priority);
}

// Assign a Task to a Node
Task* assign_task(TaskManager* manager, Node* node) {
    if (!manager || manager->task_count == 0 || !node) return NULL;

    Task* best_task = NULL;
    int best_index = -1;

    for (uint64_t i = 0; i < manager->task_count; i++) {
        Task* current_task = &manager->task_queue[i];
        if (current_task->energy_required <= node->energy && (!best_task || current_task->priority > best_task->priority)) {
            best_task = current_task;
            best_index = i;
        }
    }

    if (best_task) {
        for (uint64_t i = best_index; i < manager->task_count - 1; i++) {
            manager->task_queue[i] = manager->task_queue[i + 1];
        }
        manager->task_count--;

        printf("Task %lu assigned to Node %lu.\n", best_task->task_id, node->id);
        return best_task;
    }

    printf("No suitable task found for Node %lu.\n", node->id);
    return NULL;
}

// Destroy the Task Manager
void destroy_task_manager(TaskManager* manager) {
    if (manager) {
        free(manager->task_queue);
        free(manager);
        printf("Task Manager destroyed.\n");
    }
}
