#!/bin/bash

# Define the root directory
ROOT_DIR="ai_systems"

# Iterate through all .c files in the project
find "$ROOT_DIR" -name "*.c" | while read -r file; do
    echo "Processing $file..."

    # Update #include statements to reference correct relative paths
    sed -i 's/#include "\(.*\)_H"/#include "..\/\1\/\U\1_H"/g' "$file"

done

echo "All include paths have been updated."
