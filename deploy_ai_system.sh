#!/bin/bash

# 🚀 AI SYSTEM DEPLOYMENT SCRIPT
# This script automates the AWS + Kubernetes AI deployment

# --- CONFIGURATION ---
AWS_REGION="us-east-1"
S3_BUCKET_AI="ai-insights-bucket-$RANDOM"
DYNAMODB_TABLE="AI_NodeStatusTable"
IAM_ROLE_NAME="AIProcessingRole"
INSTANCE_TYPE="g5.2xlarge"  # GPU instance for AI models
LAMBDA_FUNCTION_NAME="AI_NodeProcessor"
SECURITY_GROUP_NAME="AI-SecurityGroup"
KEY_PAIR_NAME="AI-Deployment-Key"
EC2_AMI="ami-09e67e426f25ce0d7"  # Amazon Linux 2
K8S_NAMESPACE="ai-system"
K8S_REPLICAS=3
GPU_ENABLED=true
KUBE_CONFIG="$HOME/.kube/config"

# --- ERROR HANDLING ---
set -e
trap 'echo "⚠️ ERROR at line $LINENO: $BASH_COMMAND" && exit 1' ERR

# --- INSTALL DEPENDENCIES ---
echo "🔧 Installing dependencies..."
sudo apt update && sudo apt install -y awscli kubectl jq docker.io

# --- CONFIGURE AWS ---
echo "🔐 Configuring AWS..."
aws configure set region $AWS_REGION

# --- CREATE S3 BUCKET ---
echo "🪣 Creating Secure S3 Bucket: $S3_BUCKET_AI..."
aws s3api create-bucket --bucket "$S3_BUCKET_AI" --region "$AWS_REGION" \
    --create-bucket-configuration LocationConstraint="$AWS_REGION"

# Secure the bucket
aws s3api put-bucket-encryption --bucket "$S3_BUCKET_AI" \
    --server-side-encryption-configuration '{
        "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
    }'

# --- CREATE DYNAMODB TABLE ---
echo "📊 Creating DynamoDB Table: $DYNAMODB_TABLE..."
aws dynamodb create-table --table-name "$DYNAMODB_TABLE" \
    --attribute-definitions AttributeName=NodeID,AttributeType=S \
    --key-schema AttributeName=NodeID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

# --- CREATE IAM ROLE ---
echo "🔐 Creating IAM Role: $IAM_ROLE_NAME..."
aws iam create-role --role-name "$IAM_ROLE_NAME" \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": ["ec2.amazonaws.com", "lambda.amazonaws.com"]},
            "Action": "sts:AssumeRole"
        }]
    }'

# Attach necessary policies
aws iam attach-role-policy --role-name "$IAM_ROLE_NAME" --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam attach-role-policy --role-name "$IAM_ROLE_NAME" --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam attach-role-policy --role-name "$IAM_ROLE_NAME" --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess

ROLE_ARN=$(aws iam get-role --role-name "$IAM_ROLE_NAME" --query 'Role.Arn' --output text)

# --- CREATE SECURITY GROUP ---
echo "🔒 Creating Security Group: $SECURITY_GROUP_NAME..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group --group-name "$SECURITY_GROUP_NAME" \
    --description "Security group for AI Processing" --query 'GroupId' --output text)

aws ec2 authorize-security-group-ingress --group-id "$SECURITY_GROUP_ID" --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id "$SECURITY_GROUP_ID" --protocol tcp --port 5000 --cidr 0.0.0.0/0

# --- CREATE EC2 INSTANCE ---
echo "🚀 Launching EC2 Instance..."
INSTANCE_ID=$(aws ec2 run-instances --image-id "$EC2_AMI" --instance-type "$INSTANCE_TYPE" \
    --iam-instance-profile Name="$IAM_ROLE_NAME" --security-group-ids "$SECURITY_GROUP_ID" \
    --key-name "$KEY_PAIR_NAME" --query 'Instances[0].InstanceId' --output text)

# --- DEPLOY KUBERNETES CLUSTER ---
echo "🔧 Deploying Kubernetes Cluster..."
curl -s https://get.k3s.io | sh
kubectl create namespace $K8S_NAMESPACE

# --- DEPLOY MONITORING (Prometheus & Grafana) ---
echo "📊 Deploying Monitoring System..."
kubectl apply -f monitoring/prometheus-deployment.yaml
kubectl apply -f monitoring/grafana-deployment.yaml

# --- DEPLOY MODEL SERVERS ---
echo "🧠 Deploying AI Model Servers..."
kubectl apply -f k8s/model-server.yaml
kubectl apply -f k8s/security-system.yaml
kubectl apply -f k8s/api-gateway.yaml

# --- CONFIGURE AUTOSCALING ---
echo "⚙️ Configuring Autoscaling..."
kubectl apply -f k8s/hpa-model.yaml
kubectl apply -f k8s/hpa-security.yaml

# --- DEPLOY AI SYSTEM TO EC2 ---
echo "🧠 Deploying AI System to EC2..."
aws s3 cp ai_system.zip s3://$S3_BUCKET_AI/
ssh -i "$KEY_PAIR_NAME.pem" ec2-user@$INSTANCE_ID << EOF
  sudo yum install -y python3-pip
  pip3 install boto3 numpy flask
  aws s3 cp s3://$S3_BUCKET_AI/ai_system.zip /home/ec2-user/
  unzip /home/ec2-user/ai_system.zip
  python3 /home/ec2-user/start_ai.py &
EOF

# --- DEPLOY LAMBDA FUNCTION ---
echo "🔄 Deploying AWS Lambda Function..."
ZIP_FILE="lambda_function.zip"
zip -j "$ZIP_FILE" ./lambda_function.py

aws lambda create-function --function-name "$LAMBDA_FUNCTION_NAME" \
    --runtime python3.9 --role "$ROLE_ARN" --handler lambda_function.lambda_handler \
    --timeout 300 --memory-size 1024 --zip-file fileb://$ZIP_FILE

# --- FINAL VERIFICATION ---
echo "✅ Deployment Completed Successfully!"
kubectl get pods -n $K8S_NAMESPACE
aws s3 ls s3://$S3_BUCKET_AI/
aws dynamodb describe-table --table-name $DYNAMODB_TABLE
