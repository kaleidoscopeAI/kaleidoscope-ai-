#!/usr/bin/env bash
#
# aws_deploy_kaleidoscope.sh
# --------------------------
# A single comprehensive script that:
# 1) Creates or reuses a key pair.
# 2) Creates or reuses a security group.
# 3) Launches an EC2 instance with user data to install Python, pip, etc.
# 4) Waits until the instance is running.
# 5) SCPs (uploads) your local Kaleidoscope AI code to the EC2 instance.
# 6) Provides an SSH command to connect, and optionally runs your Python code.
#
# REQUIREMENTS:
# - AWS CLI installed and configured (aws configure).
# - This script is run on your local Ubuntu machine.
#
# USAGE:
#   chmod +x aws_deploy_kaleidoscope.sh
#   ./aws_deploy_kaleidoscope.sh
#
# Feel free to adapt paths, package installs, AMI, instance type, etc.

set -e  # Exit immediately if a command exits with a non-zero status

##############################################################################
# 0. Configuration Variables (EDIT THESE)
##############################################################################

REGION="us-east-1"
# For Amazon Linux 2 in us-east-1 (adjust to latest / your region):
AMI_ID="ami-08c40ec9ead489470"
INSTANCE_TYPE="t2.micro"

KEY_NAME="KaleidoscopeKey"    # Name of the key pair
SECURITY_GROUP_NAME="KaleidoscopeSG"
SECURITY_GROUP_DESC="Security group for Kaleidoscope AI"

# Local directory containing your Kaleidoscope AI code
# e.g. "/home/user/projects/kaleidoscope_ai"
LOCAL_CODE_DIR="/path/to/your/kaleidoscope_ai"

# File or command you want to run once you've uploaded. e.g. main.py
REMOTE_RUN_COMMAND="python3 kaleidoscope_ai/main.py"

##############################################################################
# 1. Create (or reuse) the Key Pair
##############################################################################

echo ">>> Checking for existing key pair: ${KEY_NAME}"
if ! aws ec2 describe-key-pairs --key-name "${KEY_NAME}" --region "${REGION}" >/dev/null 2>&1; then
  echo ">>> Creating a new Key Pair: ${KEY_NAME}"
  aws ec2 create-key-pair \
    --key-name "${KEY_NAME}" \
    --region "${REGION}" \
    --query 'KeyMaterial' \
    --output text > "${KEY_NAME}.pem"
  chmod 400 "${KEY_NAME}.pem"
  echo ">>> Created key '${KEY_NAME}' and saved to '${KEY_NAME}.pem'"
else
  echo ">>> Key Pair '${KEY_NAME}' already exists. Reusing it."
fi

##############################################################################
# 2. Create (or reuse) the Security Group
##############################################################################

echo ">>> Checking for existing Security Group: ${SECURITY_GROUP_NAME}"
SG_ID=$(aws ec2 describe-security-groups --region "${REGION}" \
        --filters "Name=group-name,Values=${SECURITY_GROUP_NAME}" \
        --query 'SecurityGroups[0].GroupId' \
        --output text 2>/dev/null || true)

if [[ "${SG_ID}" == "None" || -z "${SG_ID}" ]]; then
  echo ">>> Creating a new Security Group: ${SECURITY_GROUP_NAME}"
  SG_ID=$(aws ec2 create-security-group \
    --group-name "${SECURITY_GROUP_NAME}" \
    --description "${SECURITY_GROUP_DESC}" \
    --region "${REGION}" \
    --query 'GroupId' \
    --output text)
  echo ">>> Created Security Group with ID: ${SG_ID}"

  # Allow SSH (22) from anywhere - NOT RECOMMENDED for production
  aws ec2 authorize-security-group-ingress \
    --group-id "${SG_ID}" \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 \
    --region "${REGION}"

  # OPTIONAL: Allow HTTP (port 80) for a web server
  # Uncomment if needed
  # aws ec2 authorize-security-group-ingress \
  #   --group-id "${SG_ID}" \
  #   --protocol tcp \
  #   --port 80 \
  #   --cidr 0.0.0.0/0 \
  #   --region "${REGION}"
else
  echo ">>> Found existing Security Group: ${SG_ID}"
fi

##############################################################################
# 3. Create a User Data Script to install Python/pip on the EC2
##############################################################################

echo ">>> Creating user_data.txt to install Python3, pip, etc."

cat <<'EOF' > user_data.txt
#!/bin/bash
# user-data script for Amazon Linux 2
# 1) Update packages
yum update -y
# 2) Install Python3, git
yum install -y python3 git
# 3) Upgrade pip & install common Python libraries
pip3 install --upgrade pip
pip3 install numpy scipy networkx joblib scikit-learn torch --no-cache-dir
EOF

##############################################################################
# 4. Launch the EC2 Instance
##############################################################################

echo ">>> Launching EC2 instance in region: ${REGION}"

INSTANCE_ID=$(aws ec2 run-instances \
  --image-id "${AMI_ID}" \
  --count 1 \
  --instance-type "${INSTANCE_TYPE}" \
  --key-name "${KEY_NAME}" \
  --security-group-ids "${SG_ID}" \
  --user-data file://user_data.txt \
  --region "${REGION}" \
  --query 'Instances[0].InstanceId' \
  --output text)

echo ">>> EC2 instance requested: ${INSTANCE_ID}"

echo ">>> Waiting for instance to enter 'running' state..."
aws ec2 wait instance-running --instance-ids "${INSTANCE_ID}" --region "${REGION}"

##############################################################################
# 5. Get Public IP or DNS and Display Connection Info
##############################################################################

PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids "${INSTANCE_ID}" \
  --region "${REGION}" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

PUBLIC_DNS=$(aws ec2 describe-instances \
  --instance-ids "${INSTANCE_ID}" \
  --region "${REGION}" \
  --query 'Reservations[0].Instances[0].PublicDnsName' \
  --output text)

echo "---------------------------------------------------------"
echo ">>> EC2 is up and running!"
echo "Instance ID: ${INSTANCE_ID}"
echo "Public IP:  ${PUBLIC_IP}"
echo "Public DNS: ${PUBLIC_DNS}"
echo "---------------------------------------------------------"

##############################################################################
# 6. SCP (Upload) Your Local Kaleidoscope AI Code to the EC2 Instance
##############################################################################

if [ ! -d "${LOCAL_CODE_DIR}" ]; then
  echo "WARNING: Local code directory '${LOCAL_CODE_DIR}' not found. Skipping upload."
  UPLOAD_OK="false"
else
  echo ">>> Uploading local code from '${LOCAL_CODE_DIR}' to EC2 at /home/ec2-user/kaleidoscope_ai"
  # The default user for Amazon Linux 2 is 'ec2-user'
  scp -r -o StrictHostKeyChecking=no -i "${KEY_NAME}.pem" "${LOCAL_CODE_DIR}" ec2-user@"${PUBLIC_IP}":/home/ec2-user/
  echo ">>> Upload complete!"
  UPLOAD_OK="true"
fi

##############################################################################
# 7. (Optional) Run your code on the EC2 instance
##############################################################################

if [ "${UPLOAD_OK}" = "true" ]; then
  echo ">>> Attempting to run your code on the EC2 instance: ${REMOTE_RUN_COMMAND}"
  ssh -o StrictHostKeyChecking=no -i "${KEY_NAME}.pem" ec2-user@"${PUBLIC_IP}" "${REMOTE_RUN_COMMAND}" || {
    echo "WARNING: Remote run command failed. You can SSH in manually."
  }
fi

##############################################################################
# 8. Final Info
##############################################################################

echo "---------------------------------------------------------"
echo ">>> Done!"
echo "You can SSH into the instance with the command below:"
echo "ssh -i \"${KEY_NAME}.pem\" ec2-user@${PUBLIC_IP}"
echo "---------------------------------------------------------"

