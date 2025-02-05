#!/bin/bash

# 🚀 Automated File System Setup for AWS-Kaleidoscope
# This script organizes files and prepares for deployment.

# --- Define Project Directories ---
PROJECT_ROOT="$HOME/Desktop/aws-kaleidoscope"
CODE_DIR="$PROJECT_ROOT/jg"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
DEPLOY_DIR="$PROJECT_ROOT/deploy"
MODELS_DIR="$PROJECT_ROOT/models"
PIPELINES_DIR="$PROJECT_ROOT/pipelines"
SECURITY_DIR="$PROJECT_ROOT/security"
MONITORING_DIR="$PROJECT_ROOT/monitoring"
TRAINING_DIR="$PROJECT_ROOT/training"
OPTIMIZATION_DIR="$PROJECT_ROOT/optimization"
BACKUP_DIR="$PROJECT_ROOT/backup"
ARCHIVE_FILE="$PROJECT_ROOT/kaleidoscope_ai.tar.gz"

echo "📁 Setting up file system structure..."

# --- Create Directories ---
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$DEPLOY_DIR"
mkdir -p "$MODELS_DIR"
mkdir -p "$PIPELINES_DIR"
mkdir -p "$SECURITY_DIR"
mkdir -p "$MONITORING_DIR"
mkdir -p "$TRAINING_DIR"
mkdir -p "$OPTIMIZATION_DIR"
mkdir -p "$BACKUP_DIR"

# --- Move Deployment Scripts ---
echo "🚀 Organizing deployment scripts..."
mv "$CODE_DIR/deploy_ai_system.sh" "$DEPLOY_DIR/"
mv "$CODE_DIR/deploy-full_ai_system.sh" "$DEPLOY_DIR/"
mv "$CODE_DIR/deploy_free_tier_ai.sh" "$DEPLOY_DIR/"
mv "$CODE_DIR/setup_aws.sh" "$DEPLOY_DIR/"

# --- Move AI Processing & Core System Scripts ---
echo "🧠 Organizing core AI processing scripts..."
mv "$CODE_DIR/adaptive_memory.py" "$MODELS_DIR/"
mv "$CODE_DIR/ai_insight_processing.py" "$MODELS_DIR/"
mv "$CODE_DIR/aws_scalability_optimization.py" "$MODELS_DIR/"
mv "$CODE_DIR/chatbot_ai.py" "$MODELS_DIR/"
mv "$CODE_DIR/chatbot.py" "$MODELS_DIR/"
mv "$CODE_DIR/core-system.py" "$MODELS_DIR/"
mv "$CODE_DIR/genetic_optimizer.py" "$MODELS_DIR/"
mv "$CODE_DIR/prediction_engine.py" "$MODELS_DIR/"
mv "$CODE_DIR/prediction_engine.py.txt" "$MODELS_DIR/"

# --- Move Pipelines & Data Processing ---
echo "📊 Organizing data pipelines..."
mv "$CODE_DIR/data-pipeline.py" "$PIPELINES_DIR/"
mv "$CODE_DIR/pipeline_integration.py" "$PIPELINES_DIR/"
mv "$CODE_DIR/membrane.py" "$PIPELINES_DIR/"

# --- Move Security Modules ---
echo "🔐 Organizing security scripts..."
mv "$CODE_DIR/security-engine.py" "$SECURITY_DIR/"
mv "$CODE_DIR/security-layer.txt" "$SECURITY_DIR/"
mv "$CODE_DIR/security-layer-continued.py" "$SECURITY_DIR/"
mv "$CODE_DIR/security-layer (1).txt" "$SECURITY_DIR/"

# --- Move Monitoring & Logging ---
echo "📡 Organizing monitoring & logging scripts..."
mv "$CODE_DIR/monitoring-system.txt" "$MONITORING_DIR/"
mv "$CODE_DIR/monitoring-system-continued.txt" "$MONITORING_DIR/"
mv "$CODE_DIR/monitoring-system-final.py" "$MONITORING_DIR/"
mv "$CODE_DIR/real_time_monitor.py" "$MONITORING_DIR/"
mv "$CODE_DIR/real_time_monitoring.py" "$MONITORING_DIR/"

# --- Move Training Modules ---
echo "🧬 Organizing AI training scripts..."
mv "$CODE_DIR/training-system.txt" "$TRAINING_DIR/"
mv "$CODE_DIR/training-system (1).txt" "$TRAINING_DIR/"
mv "$CODE_DIR/training-system (2).txt" "$TRAINING_DIR/"
mv "$CODE_DIR/training-system-continued.py" "$TRAINING_DIR/"
mv "$CODE_DIR/training-system-continued (1).py" "$TRAINING_DIR/"

# --- Move Optimization Modules ---
echo "📈 Organizing optimization scripts..."
mv "$CODE_DIR/optimization-service.txt" "$OPTIMIZATION_DIR/"
mv "$CODE_DIR/value-analysis.py" "$OPTIMIZATION_DIR/"
mv "$CODE_DIR/performance-test.py" "$OPTIMIZATION_DIR/"

# --- Backup & Archive Everything ---
echo "📦 Creating project backup..."
tar -czf "$ARCHIVE_FILE" -C "$PROJECT_ROOT" .

echo "✅ File system setup complete!"
echo "📁 Organized Project Structure:"
ls -R "$PROJECT_ROOT"
