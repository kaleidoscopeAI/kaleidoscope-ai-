#!/bin/bash

# Create virtual environment
python3 -m venv qdd_env

# Activate environment
source qdd_env/bin/activate

# Install requirements
pip install -r requirements.txt

echo "Installation complete. Run 'source qdd_env/bin/activate' to activate the environment."
