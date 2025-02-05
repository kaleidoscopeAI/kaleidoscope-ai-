#!/bin/bash

# AI System Build, Execution, and Monitor Manager
# Combines setup, compilation, and real-time execution with monitoring and visualization.

# Define directories and source files
SOURCE_DIR="ai_system"
BUILD_DIR="build"
EXECUTABLE="ai_system_main"
DATASET_DIR="datasets"
INSIGHTS_DIR="insights"
LOG_FILE="build.log"

echo "---- AI System Build, Execution, and Monitor Manager ----"

# Step 1: Clean previous builds
echo "Cleaning previous builds..."
rm -rf $BUILD_DIR $INSIGHTS_DIR
mkdir -p $BUILD_DIR $DATASET_DIR $INSIGHTS_DIR
rm -f $LOG_FILE
echo "Clean complete."

# Step 2: Copy source files to build directory
echo "Copying source files to build directory..."
cp -r $SOURCE_DIR/* $BUILD_DIR

# Step 3: Navigate to build directory
cd $BUILD_DIR || { echo "Failed to navigate to build directory"; exit 1; }

# Step 4: Compile the system
echo "Compiling the AI system..."
gcc -o $EXECUTABLE \
    core/node_core.c \
    core/membrane.c \
    engines/kaleidoscope_engine.c \
    engines/mirrored_engine.c \
    task_management/task_manager.c \
    memory/memory_graph.c \
    ethics/global_ethics_system.c \
    predictive/predictive_modeling.c \
    predictive/anomaly_detection.c \
    learning/learning_feedback.c \
    simulation/behavior_simulation.c \
    collaboration/collaboration_nodes.c \
    optimization/resource_optimization.c \
    ingestion/data_ingestion.c \
    visualization/visualization_tools.c \
    environment/environment_simulation.c \
    diagnostics/self_diagnostic.c \
    master_integration/master_integration.c \
    -lm -o $EXECUTABLE 2>> ../$LOG_FILE

if [ $? -ne 0 ]; then
    echo "Build failed. Check the log file for details: $LOG_FILE"
    exit 1
fi

echo "Compilation successful. Executable created: $EXECUTABLE"

# Step 5: Continuous Execution with Real-Time Visualization
echo "Starting AI System in Continuous Mode..."
while true; do
    echo "Monitoring datasets in $DATASET_DIR..."
    
    # Check for new datasets
    for dataset in $DATASET_DIR/*; do
        if [ -f "$dataset" ]; then
            echo "Processing dataset: $dataset"
            
            # Execute the AI system with the dataset
            ./$EXECUTABLE "$dataset" "$INSIGHTS_DIR" | tee -a ../$LOG_FILE | while read line; do
                # Real-Time Updates in Terminal
                if [[ "$line" == *"Cycle"* ]]; then
                    echo -e "\033[1;34m$line\033[0m" # Highlight cycles in blue
                elif [[ "$line" == *"Task"* ]]; then
                    echo -e "\033[1;32m$line\033[0m" # Highlight task progress in green
                elif [[ "$line" == *"Error"* ]]; then
                    echo -e "\033[1;31m$line\033[0m" # Highlight errors in red
                else
                    echo "$line" # Default formatting for other outputs
                fi
            done
            
            if [ $? -ne 0 ]; then
                echo "Execution failed for dataset: $dataset. Check log file for details."
            else
                echo "Dataset processed successfully. Insights saved to $INSIGHTS_DIR."
                mv "$dataset" "$dataset.processed"
            fi
        fi
    done
    
    # Sleep before the next cycle
    echo "Waiting for new datasets..."
    sleep 10
done

echo "AI System terminated manually."
