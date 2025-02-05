#include "kaleidoscope_engine.h"
#include <stdlib.h>
#include <stdio.h>

// Initialize the Kaleidoscope Engine
KaleidoscopeEngine* init_kaleidoscope_engine(void) {
    KaleidoscopeEngine* engine = (KaleidoscopeEngine*)malloc(sizeof(KaleidoscopeEngine));
    if (!engine) return NULL;

    engine->recognizer = init_pattern_recognizer();
    engine->optimizer = init_optimizer();

    if (!engine->recognizer || !engine->optimizer) {
        destroy_kaleidoscope_engine(engine);
        return NULL;
    }

    printf("Kaleidoscope Engine initialized.\n");
    return engine;
}

// Process a Task in the Kaleidoscope Engine
ProcessedData* process_task(KaleidoscopeEngine* engine, RawData* task_data) {
    if (!engine || !task_data) {
        printf("Invalid input to Kaleidoscope Engine.\n");
        return NULL;
    }

    printf("Processing task in Kaleidoscope Engine...\n");

    // Recognize patterns
    ProcessedData* patterns = engine->recognizer->recognize(task_data);
    if (!patterns) {
        printf("Pattern recognition failed.\n");
        return NULL;
    }

    // Optimize recognized patterns
    engine->optimizer->optimize(patterns);

    printf("Task processed successfully.\n");
    return patterns;
}

// Destroy the Kaleidoscope Engine
void destroy_kaleidoscope_engine(KaleidoscopeEngine* engine) {
    if (engine) {
        if (engine->recognizer) destroy_pattern_recognizer(engine->recognizer);
        if (engine->optimizer) destroy_optimizer(engine->optimizer);
        free(engine);
        printf("Kaleidoscope Engine destroyed.\n");
    }
}
