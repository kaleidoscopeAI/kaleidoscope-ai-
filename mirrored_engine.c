#include "mirrored_engine.h"
#include <stdlib.h>
#include <stdio.h>

// Initialize the Mirrored Engine
MirroredEngine* init_mirrored_engine(void) {
    MirroredEngine* engine = (MirroredEngine*)malloc(sizeof(MirroredEngine));
    if (!engine) return NULL;

    engine->validator = init_validator();
    engine->knowledge_sharer = init_knowledge_sharer();

    if (!engine->validator || !engine->knowledge_sharer) {
        destroy_mirrored_engine(engine);
        return NULL;
    }

    printf("Mirrored Engine initialized.\n");
    return engine;
}

// Validate Insights
ValidatedData* validate_insights(MirroredEngine* engine, ProcessedData* insights) {
    if (!engine || !insights) {
        printf("Invalid input to Mirrored Engine for validation.\n");
        return NULL;
    }

    printf("Validating insights in Mirrored Engine...\n");

    // Perform validation
    ValidatedData* validated = engine->validator->validate(insights);
    if (!validated) {
        printf("Insight validation failed.\n");
        return NULL;
    }

    printf("Insights validated successfully.\n");
    return validated;
}

// Share Validated Knowledge
void share_validated_knowledge(MirroredEngine* engine, ValidatedData* validated) {
    if (!engine || !validated) {
        printf("Invalid input to Mirrored Engine for sharing knowledge.\n");
        return;
    }

    printf("Sharing validated knowledge in Mirrored Engine...\n");

    // Share the knowledge across nodes or systems
    engine->knowledge_sharer->share(validated);
}

// Destroy the Mirrored Engine
void destroy_mirrored_engine(MirroredEngine* engine) {
    if (engine) {
        if (engine->validator) destroy_validator(engine->validator);
        if (engine->knowledge_sharer) destroy_knowledge_sharer(engine->knowledge_sharer);
        free(engine);
        printf("Mirrored Engine destroyed.\n");
    }
}
