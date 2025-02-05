#include "data_ingestion.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

// Initialize the Data Ingestion Layer
DataIngestionLayer* init_data_ingestion_layer(uint64_t max_entries) {
    DataIngestionLayer* layer = (DataIngestionLayer*)malloc(sizeof(DataIngestionLayer));
    if (!layer) return NULL;

    layer->text_data = (char**)malloc(sizeof(char*) * max_entries);
    layer->numerical_data = (double**)malloc(sizeof(double*) * max_entries);
    layer->visual_data = (char**)malloc(sizeof(char*) * max_entries);

    if (!layer->text_data || !layer->numerical_data || !layer->visual_data) {
        free(layer->text_data);
        free(layer->numerical_data);
        free(layer->visual_data);
        free(layer);
        return NULL;
    }

    layer->text_count = 0;
    layer->numerical_count = 0;
    layer->visual_count = 0;
    layer->max_entries = max_entries;

    printf("Data Ingestion Layer initialized with capacity for %lu entries.\n", max_entries);
    return layer;
}

// Ingest Text Data
void ingest_text(DataIngestionLayer* layer, const char* text) {
    if (!layer || layer->text_count >= layer->max_entries) {
        printf("Data Ingestion Layer: Cannot ingest text. Capacity reached or uninitialized layer.\n");
        return;
    }

    layer->text_data[layer->text_count++] = strdup(text);
    printf("Ingested text: %s\n", text);
}

// Ingest Numerical Data
void ingest_numerical(DataIngestionLayer* layer, double* numbers, uint64_t count) {
    if (!layer || layer->numerical_count >= layer->max_entries) {
        printf("Data Ingestion Layer: Cannot ingest numerical data. Capacity reached or uninitialized layer.\n");
        return;
    }

    double* normalized = (double*)malloc(sizeof(double) * count);
    if (!normalized) return;

    // Normalize numerical data
    double min = numbers[0], max = numbers[0];
    for (uint64_t i = 1; i < count; i++) {
        if (numbers[i] < min) min = numbers[i];
        if (numbers[i] > max) max = numbers[i];
    }

    for (uint64_t i = 0; i < count; i++) {
        normalized[i] = (numbers[i] - min) / (max - min);
    }

    layer->numerical_data[layer->numerical_count++] = normalized;
    printf("Ingested numerical data.\n");
}

// Ingest Visual Data
void ingest_visual(DataIngestionLayer* layer, const char* visual_input) {
    if (!layer || layer->visual_count >= layer->max_entries) {
        printf("Data Ingestion Layer: Cannot ingest visual data. Capacity reached or uninitialized layer.\n");
        return;
    }

    layer->visual_data[layer->visual_count++] = strdup(visual_input);
    printf("Ingested visual data: %s\n", visual_input);
}

// Retrieve and Display Ingested Data
void display_ingested_data(DataIngestionLayer* layer) {
    if (!layer) return;

    printf("\n--- Ingested Data ---\n");
    printf("Text Data:\n");
    for (uint64_t i = 0; i < layer->text_count; i++) {
        printf("  %s\n", layer->text_data[i]);
    }

    printf("Numerical Data:\n");
    for (uint64_t i = 0; i < layer->numerical_count; i++) {
        printf("  Entry %lu: ", i + 1);
        for (uint64_t j = 0; j < sizeof(layer->numerical_data[i]) / sizeof(double); j++) {
            printf("%.2f ", layer->numerical_data[i][j]);
        }
        printf("\n");
    }

    printf("Visual Data:\n");
    for (uint64_t i = 0; i < layer->visual_count; i++) {
        printf("  %s\n", layer->visual_data[i]);
    }
}

// Destroy the Data Ingestion Layer
void destroy_data_ingestion_layer(DataIngestionLayer* layer) {
    if (layer) {
        for (uint64_t i = 0; i < layer->text_count; i++) {
            free(layer->text_data[i]);
        }
        for (uint64_t i = 0; i < layer->numerical_count; i++) {
            free(layer->numerical_data[i]);
        }
        for (uint64_t i = 0; i < layer->visual_count; i++) {
            free(layer->visual_data[i]);
        }

        free(layer->text_data);
        free(layer->numerical_data);
        free(layer->visual_data);
        free(layer);
        printf("Data Ingestion Layer destroyed.\n");
    }
}
