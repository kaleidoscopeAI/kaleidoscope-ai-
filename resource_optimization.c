#include "resource_optimization.h"
#include <stdlib.h>
#include <stdio.h>

// Initialize the Resource Optimizer
ResourceOptimizer* init_resource_optimizer(uint64_t total_energy, uint64_t total_memory) {
    ResourceOptimizer* optimizer = (ResourceOptimizer*)malloc(sizeof(ResourceOptimizer));
    if (!optimizer) return NULL;

    optimizer->total_energy = total_energy;
    optimizer->total_memory = total_memory;
    optimizer->allocated_energy = 0;
    optimizer->allocated_memory = 0;

    printf("Resource Optimizer initialized with %lu energy and %lu memory.\n", total_energy, total_memory);
    return optimizer;
}

// Allocate Resources to a Node
void allocate_resources(ResourceOptimizer* optimizer, Node* node, uint64_t energy_needed, uint64_t memory_needed) {
    if (!optimizer || !node) return;

    if (optimizer->total_energy - optimizer->allocated_energy >= energy_needed &&
        optimizer->total_memory - optimizer->allocated_memory >= memory_needed) {

        node->energy += energy_needed;
        optimizer->allocated_energy += energy_needed;

        node->memory_size += memory_needed;
        optimizer->allocated_memory += memory_needed;

        printf("Allocated %lu energy and %lu memory to Node %lu.\n", energy_needed, memory_needed, node->id);
    } else {
        printf("Insufficient resources to allocate to Node %lu.\n", node->id);
    }
}

// Release Resources
void release_resources(ResourceOptimizer* optimizer, uint64_t energy_released, uint64_t memory_released) {
    if (!optimizer) return;

    optimizer->allocated_energy -= energy_released;
    optimizer->allocated_memory -= memory_released;

    printf("Released %lu energy and %lu memory.\n", energy_released, memory_released);
}

// Optimize Resources Across Nodes
void optimize_node_resources(ResourceOptimizer* optimizer, Node* nodes[], uint64_t node_count) {
    if (!optimizer || !nodes || node_count == 0) return;

    printf("Optimizing resources across %lu nodes...\n", node_count);

    uint64_t energy_per_node = (optimizer->total_energy - optimizer->allocated_energy) / node_count;
    uint64_t memory_per_node = (optimizer->total_memory - optimizer->allocated_memory) / node_count;

    for (uint64_t i = 0; i < node_count; i++) {
        if (nodes[i]->is_active) {
            allocate_resources(optimizer, nodes[i], energy_per_node, memory_per_node);
        }
    }
}

// Destroy the Resource Optimizer
void destroy_resource_optimizer(ResourceOptimizer* optimizer) {
    if (optimizer) {
        free(optimizer);
        printf("Resource Optimizer destroyed.\n");
    }
}
