#!/bin/bash

echo "🔐 Setting Up AWS Credentials..."
export AWS_ACCESS_KEY_ID="AKIA4WJPWX757RLAGXU7"
export AWS_SECRET_ACCESS_KEY="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"
export AWS_DEFAULT_REGION="us-east-2"

aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set region $AWS_DEFAULT_REGION
aws configure set output json

echo "✅ AWS Credentials Configured."

echo "🛠️ Creating S3 Bucket for AI Storage..."
BUCKET_NAME="ai-insights-bucket-872515289083"
aws s3api create-bucket --bucket $BUCKET_NAME --region us-east-2 --create-bucket-configuration LocationConstraint=us-east-2
echo "✅ S3 Bucket Created: $BUCKET_NAME"

echo "📊 Checking for DynamoDB Table..."
TABLE_NAME="AI_NodeStatusTable"
EXISTING_TABLE=$(aws dynamodb list-tables --query "TableNames" --output json | grep $TABLE_NAME)
if [[ -z "$EXISTING_TABLE" ]]; then
    aws dynamodb create-table --table-name $TABLE_NAME \
        --attribute-definitions AttributeName=NodeId,AttributeType=S \
        --key-schema AttributeName=NodeId,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST
    echo "✅ DynamoDB Table Created: $TABLE_NAME"
else
    echo "✅ DynamoDB Table Already Exists."
fi

echo "🔐 Creating Security Group..."
SECURITY_GROUP_NAME="AI-SecurityGroup"
VPC_ID=$(aws ec2 describe-vpcs --query "Vpcs[0].VpcId" --output text)
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --query "SecurityGroups[?GroupName=='$SECURITY_GROUP_NAME'].GroupId" --output text)

if [[ -z "$SECURITY_GROUP_ID" ]]; then
    SECURITY_GROUP_ID=$(aws ec2 create-security-group --group-name $SECURITY_GROUP_NAME --description "AI Security Group" --vpc-id $VPC_ID --query 'GroupId' --output text)
    echo "✅ Security Group Created: $SECURITY_GROUP_ID"
else
    echo "✅ Security Group Already Exists: $SECURITY_GROUP_ID"
fi

echo "🔓 Configuring Firewall Rules..."
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 22 --cidr 0.0.0.0/0 || true
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 5000 --cidr 0.0.0.0/0 || true
echo "✅ Security Group Rules Configured."

echo "🔑 Creating EC2 Key Pair..."
KEY_NAME="KaleidoscopeKey"
aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > $KEY_NAME.pem
chmod 400 $KEY_NAME.pem
echo "✅ Key Pair Created."

echo "🚀 Launching EC2 Instance for AI System..."
INSTANCE_ID=$(aws ec2 run-instances --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t2.micro --key-name $KEY_NAME --security-group-ids $SECURITY_GROUP_ID \
    --iam-instance-profile Name=AIProcessingRole \
    --user-data file://setup_ai_instance.sh \
    --query "Instances[0].InstanceId" --output text)

echo "🕒 Waiting for EC2 Instance to Start..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query "Reservations[0].Instances[0].PublicIpAddress" --output text)
echo "🌍 AI System Running at: http://$PUBLIC_IP:5000"

echo "🌐 Opening AI System in Browser..."
google-chrome http://$PUBLIC_IP:5000 || xdg-open http://$PUBLIC_IP:5000

echo "🎉 AWS AI System Deployment Complete!"
