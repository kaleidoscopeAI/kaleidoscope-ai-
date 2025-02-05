#include "memory_graph.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

// Initialize the Memory Graph
MemoryGraph* init_memory_graph(uint64_t max_nodes) {
    MemoryGraph* graph = (MemoryGraph*)malloc(sizeof(MemoryGraph));
    if (!graph) return NULL;

    graph->nodes = (MemoryNode**)malloc(sizeof(MemoryNode*) * max_nodes);
    if (!graph->nodes) {
        free(graph);
        return NULL;
    }

    graph->node_count = 0;
    graph->max_nodes = max_nodes;

    printf("Memory Graph initialized with capacity for %lu nodes.\n", max_nodes);
    return graph;
}

// Create a Memory Node
MemoryNode* create_memory_node(const char* data, uint8_t importance) {
    MemoryNode* node = (MemoryNode*)malloc(sizeof(MemoryNode));
    if (!node) return NULL;

    node->data = strdup(data);
    node->importance = importance;
    node->timestamp = time(NULL);
    node->connections = NULL;
    node->connection_count = 0;

    printf("Memory Node created: '%s' (Importance: %u)\n", data, importance);
    return node;
}

// Connect Two Memory Nodes
void connect_memory_nodes(MemoryNode* node1, MemoryNode* node2) {
    if (!node1 || !node2) return;

    node1->connections = (MemoryNode**)realloc(node1->connections, sizeof(MemoryNode*) * (node1->connection_count + 1));
    node2->connections = (MemoryNode**)realloc(node2->connections, sizeof(MemoryNode*) * (node2->connection_count + 1));

    node1->connections[node1->connection_count++] = node2;
    node2->connections[node2->connection_count++] = node1;

    printf("Connected memory nodes: '%s' <-> '%s'\n", node1->data, node2->data);
}

// Add a Memory Node to the Graph
void add_memory_node(MemoryGraph* graph, MemoryNode* node) {
    if (!graph || graph->node_count >= graph->max_nodes || !node) return;

    graph->nodes[graph->node_count++] = node;
    printf("Added memory node: '%s'\n", node->data);
}

// Recall Memory by Keyword
void recall_memory(MemoryGraph* graph, const char* keyword) {
    if (!graph || !keyword) return;

    printf("Recalling memories related to keyword: '%s'\n", keyword);
    for (uint64_t i = 0; i < graph->node_count; i++) {
        if (strstr(graph->nodes[i]->data, keyword)) {
            printf("Memory Found: '%s' (Importance: %u)\n", graph->nodes[i]->data, graph->nodes[i]->importance);
        }
    }
}

// Destroy the Memory Graph
void destroy_memory_graph(MemoryGraph* graph) {
    if (graph) {
        for (uint64_t i = 0; i < graph->node_count; i++) {
            free(graph->nodes[i]->data);
            free(graph->nodes[i]->connections);
            free(graph->nodes[i]);
        }
        free(graph->nodes);
        free(graph);
        printf("Memory Graph destroyed.\n");
    }
}
