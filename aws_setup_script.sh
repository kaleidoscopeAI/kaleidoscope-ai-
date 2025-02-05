#!/bin/bash

# Advanced AWS Setup Script with Enhanced Security, Scaling, and Monitoring
# This script configures the AWS infrastructure required for the Node system.

# Variables
REGION="us-east-1"
S3_BUCKET_INSIGHTS="insights-bucket-${RANDOM}"
DYNAMODB_TABLE_NODES="NodeStatusTable"
SNS_TOPIC_NODES="NodeNotifications"
CLOUDWATCH_LOG_GROUP="/node-system/logs"
KMS_KEY_ALIAS="node-system-key"
IAM_ROLE_NAME="NodeSystemExecutionRole"

# Logging setup
LOG_FILE="/tmp/aws_setup_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

# Error Handling
error_handler() {
    echo "Error occurred in script at line: ${1}, error code: ${2}"
    exit 1
}
trap 'error_handler ${LINENO} $?' ERR

# Check AWS CLI and Credentials
check_prerequisites() {
    echo "Checking AWS CLI and credentials..."
    if ! command -v aws &> /dev/null; then
        echo "AWS CLI is not installed. Exiting."
        exit 1
    fi
    if ! aws sts get-caller-identity &> /dev/null; then
        echo "AWS credentials are not configured. Exiting."
        exit 1
    fi
}

# Create IAM Role for Execution
create_iam_role() {
    echo "Creating IAM role for execution: $IAM_ROLE_NAME"
    aws iam create-role --role-name "$IAM_ROLE_NAME" --assume-role-policy-document ' {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }' --region "$REGION" --output json

    aws iam attach-role-policy --role-name "$IAM_ROLE_NAME" --policy-arn "arn:aws:iam::aws:policy/AWSLambdaBasicExecutionRole"
    echo "IAM role created successfully."
}

# Create KMS Key for Encryption
create_kms_key() {
    echo "Creating KMS key for security..."
    KMS_KEY_ID=$(aws kms create-key --description "KMS Key for Node System Security" --region "$REGION" --output text --query 'KeyMetadata.KeyId')
    aws kms create-alias --alias-name "alias/$KMS_KEY_ALIAS" --target-key-id "$KMS_KEY_ID" --region "$REGION"
    echo "KMS key created with ID: $KMS_KEY_ID"
}

# Create S3 Bucket with Security Policies
create_s3_bucket() {
    echo "Creating secured S3 bucket: $S3_BUCKET_INSIGHTS"
    aws s3api create-bucket --bucket "$S3_BUCKET_INSIGHTS" --region "$REGION" --create-bucket-configuration LocationConstraint="$REGION"

    aws s3api put-bucket-versioning --bucket "$S3_BUCKET_INSIGHTS" --versioning-configuration Status=Enabled

    aws s3api put-bucket-encryption --bucket "$S3_BUCKET_INSIGHTS" --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'
    echo "S3 bucket $S3_BUCKET_INSIGHTS created with encryption and versioning."
}

# Create DynamoDB Table with Auto Scaling
create_dynamodb_table() {
    echo "Creating auto-scaling DynamoDB table: $DYNAMODB_TABLE_NODES"
    aws dynamodb create-table --table-name "$DYNAMODB_TABLE_NODES" --attribute-definitions AttributeName=NodeID,AttributeType=S --key-schema AttributeName=NodeID,KeyType=HASH --billing-mode PAY_PER_REQUEST --region "$REGION"
    echo "DynamoDB table $DYNAMODB_TABLE_NODES created with auto-scaling."
}

# Create SNS Topic with Enhanced Features
create_sns_topic() {
    echo "Creating SNS topic: $SNS_TOPIC_NODES"
    TOPIC_ARN=$(aws sns create-topic --name "$SNS_TOPIC_NODES" --region "$REGION" --output text --query 'TopicArn')
    echo "SNS topic created: $TOPIC_ARN"
}

# Create CloudWatch Log Group
setup_cloudwatch_logging() {
    echo "Setting up CloudWatch monitoring..."
    aws logs create-log-group --log-group-name "$CLOUDWATCH_LOG_GROUP" --region "$REGION"
    echo "CloudWatch log group created: $CLOUDWATCH_LOG_GROUP"
}

# Main Setup Function
main() {
    echo "Starting AWS infrastructure setup..."
    check_prerequisites
    create_iam_role
    create_kms_key
    create_s3_bucket
    create_dynamodb_table
    create_sns_topic
    setup_cloudwatch_logging
    echo "AWS infrastructure setup completed. Logs available at $LOG_FILE"
}

# Execute main function
main

