#include "node_core.h"
#include <stdlib.h>
#include <stdio.h>

// Initialize a Node
Node* init_node(uint64_t id) {
    Node* node = (Node*)malloc(sizeof(Node));
    if (!node) return NULL;

    node->id = id;
    node->energy = 100;
    node->memory_size = 1024; // Default memory size (1 KB)
    node->is_active = 1;
    node->learning_drive = rand() % 10;
    node->growth_drive = rand() % 10;
    node->share_drive = rand() % 10;

    printf("Node %lu initialized.\n", id);
    return node;
}

// Process Node Logic
void process_node(Node* node) {
    if (!node || !node->is_active) return;

    printf("Processing Node %lu...\n", node->id);

    // Simulate learning
    if (node->learning_drive > 5) {
        printf("Node %lu is learning...\n", node->id);
        node->energy -= 10;
    }

    // Simulate sharing
    if (node->share_drive > 5) {
        printf("Node %lu is sharing knowledge...\n", node->id);
        node->energy -= 5;
    }

    // Simulate growth
    if (node->growth_drive > 7 && node->energy > 50) {
        printf("Node %lu is growing...\n", node->id);
        node->energy -= 20;
    }

    // Check energy level
    if (node->energy <= 0) {
        printf("Node %lu is out of energy and going inactive.\n", node->id);
        node->is_active = 0;
    }
}

// Replicate a Node
Node* replicate_node(Node* parent_node, uint64_t new_id) {
    if (!parent_node || parent_node->energy < 50) {
        printf("Node %lu does not have enough energy to replicate.\n", parent_node->id);
        return NULL;
    }

    Node* new_node = init_node(new_id);
    if (new_node) {
        new_node->learning_drive = parent_node->learning_drive;
        new_node->growth_drive = parent_node->growth_drive;
        new_node->share_drive = parent_node->share_drive;
        parent_node->energy -= 50;
        printf("Node %lu replicated into Node %lu.\n", parent_node->id, new_node->id);
    }

    return new_node;
}

// Destroy a Node
void destroy_node(Node* node) {
    if (node) {
        printf("Destroying Node %lu...\n", node->id);
        free(node);
    }
}
