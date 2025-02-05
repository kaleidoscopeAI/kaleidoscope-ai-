#!/bin/bash

# Advanced AWS Configuration Script with Enhanced Security and Scaling

# Configuration Variables
REGION="us-east-1"
STACK_NAME="node-processing-stack"
S3_BUCKET_INSIGHTS="insights-bucket-${RANDOM}"
DYNAMODB_TABLE_NODES="NodeStatusTable"
SNS_TOPIC_NODES="NodeNotifications"
LAMBDA_FUNCTION_NAME="NodeProcessor"
LAMBDA_MEMORY=1024
LAMBDA_TIMEOUT=300

# IAM Role Names
LAMBDA_ROLE_NAME="node-processor-lambda-role"
EXECUTION_ROLE_NAME="node-system-execution-role"

# Logging setup
LOG_FILE="/tmp/aws_setup_$(date +%Y%m%d_%H%M%S).log"
exec 1> >(tee -a "$LOG_FILE") 2>&1

# Error handling
error_handler() {
    echo "Error occurred in script at line: ${1}, error code: ${2}"
    cleanup_on_error
    exit 1
}
trap 'error_handler ${LINENO} $?' ERR

# Cleanup function
cleanup_on_error() {
    echo "Performing cleanup..."
    aws cloudformation delete-stack --stack-name "$STACK_NAME" || true
}

# Create S3 Bucket with Security
create_s3_bucket() {
    echo "Creating S3 bucket with security: $S3_BUCKET_INSIGHTS"
    aws s3api create-bucket \
        --bucket "$S3_BUCKET_INSIGHTS" \
        --region "$REGION" \
        --create-bucket-configuration LocationConstraint="$REGION" || { echo "Failed to create S3 bucket"; exit 1; }

    aws s3api put-bucket-versioning \
        --bucket "$S3_BUCKET_INSIGHTS" \
        --versioning-configuration Status=Enabled || { echo "Failed to enable versioning on S3 bucket"; exit 1; }

    aws s3api put-bucket-encryption \
        --bucket "$S3_BUCKET_INSIGHTS" \
        --server-side-encryption-configuration '{
            "Rules": [{
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }]
        }' || { echo "Failed to enable encryption on S3 bucket"; exit 1; }
    echo "S3 bucket $S3_BUCKET_INSIGHTS created with encryption and versioning."
}

# Create DynamoDB Table with Auto Scaling
create_dynamodb_table() {
    echo "Creating DynamoDB table with auto-scaling: $DYNAMODB_TABLE_NODES"
    aws dynamodb create-table \
        --table-name "$DYNAMODB_TABLE_NODES" \
        --attribute-definitions AttributeName=NodeID,AttributeType=S \
        --key-schema AttributeName=NodeID,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region "$REGION" || { echo "Failed to create DynamoDB table"; exit 1; }

    aws application-autoscaling register-scalable-target \
        --service-namespace dynamodb \
        --resource-id "table/$DYNAMODB_TABLE_NODES" \
        --scalable-dimension "dynamodb:table:ReadCapacityUnits" \
        --min-capacity 1 \
        --max-capacity 10 || { echo "Failed to register scalable target for DynamoDB table"; exit 1; }

    aws application-autoscaling put-scaling-policy \
        --service-namespace dynamodb \
        --resource-id "table/$DYNAMODB_TABLE_NODES" \
        --scalable-dimension "dynamodb:table:ReadCapacityUnits" \
        --policy-name "AutoScalingReadCapacity" \
        --policy-type "TargetTrackingScaling" \
        --target-tracking-scaling-policy-configuration '{
            "TargetValue": 70.0,
            "PredefinedMetricSpecification": {
                "PredefinedMetricType": "DynamoDBReadCapacityUtilization"
            },
            "ScaleOutCooldown": 60,
            "ScaleInCooldown": 60
        }' || { echo "Failed to put scaling policy for DynamoDB table"; exit 1; }
    echo "DynamoDB table $DYNAMODB_TABLE_NODES created with auto-scaling."
}

# Deploy Lambda Function
deploy_lambda_function() {
    echo "Deploying Lambda function: $LAMBDA_FUNCTION_NAME"
    ZIP_FILE="lambda_function.zip"
    zip -j "$ZIP_FILE" ./lambda_function.py

    ROLE_ARN=$(aws iam get-role --role-name "$LAMBDA_ROLE_NAME" --query 'Role.Arn' --output text)

    aws lambda create-function \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --runtime python3.9 \
        --role "$ROLE_ARN" \
        --handler lambda_function.lambda_handler \
        --timeout $LAMBDA_TIMEOUT \
        --memory-size $LAMBDA_MEMORY \
        --zip-file fileb://$ZIP_FILE \
        --environment "Variables={BUCKET_NAME=$S3_BUCKET_INSIGHTS, TABLE_NAME=$DYNAMODB_TABLE_NODES, SNS_TOPIC=$SNS_TOPIC_NODES}" \
        --tracing-config Mode=Active \
        --region "$REGION" || { echo "Failed to create Lambda function"; exit 1; }
    echo "Lambda function $LAMBDA_FUNCTION_NAME deployed."
}

# Main Setup
main() {
    echo "Starting AWS configuration with security and auto-scaling..."
    create_s3_bucket
    create_dynamodb_table
    deploy_lambda_function
    echo "AWS setup complete. Logs available at $LOG_FILE"
}

# Execute main
main

