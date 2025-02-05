#!/bin/bash

echo "🔹 Setting Up AI System on EC2..."

# Install dependencies
sudo apt update -y
sudo apt install -y python3-pip python3-venv git unzip

# Set up Python environment
python3 -m venv ~/ai_env
source ~/ai_env/bin/activate
pip install --upgrade pip
pip install flask fastapi uvicorn boto3 pandas numpy scikit-learn tensorflow

# Clone AI repository (Optional)
cd ~
git clone https://github.com/your-repo/kaleidoscope-ai.git  # Change this to your actual repo
cd kaleidoscope-ai

# Run AI models and Dashboard
nohup python3 ~/Desktop/aws-kaleidoscope/jg/dashboard.py > dashboard.log 2>&1 &
nohup python3 ~/Desktop/aws-kaleidoscope/models/chatbot.py > chatbot.log 2>&1 &

echo "✅ AI System Deployed!"
