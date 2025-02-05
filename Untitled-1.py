"""
kaleidoscope/
│
├── infrastructure/
│   ├── __init__.py
│   ├── main.py                  # Main deployment script
│   ├── config.py               # Configuration management
│   ├── logging_setup.py        # Logging configuration
│   └── providers/
│       ├── __init__.py
│       ├── aws/
│       │   ├── __init__.py
│       │   ├── ec2.py          # EC2 instance management
│       │   ├── s3.py           # S3 bucket management
│       │   ├── iam.py          # IAM roles and policies
│       │   ├── monitoring.py   # CloudWatch setup
│       │   └── network.py      # VPC and networking
│       └── base.py            # Base provider interface
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Test configuration
│   └── test_infrastructure.py # Infrastructure tests
│
├── config/
│   ├── config.yaml           # Main configuration
│   └── logging.yaml         # Logging configuration
│
└── requirements.txt         # Project dependencies
"""

# infrastructure/main.py
import logging
import argparse
from typing import Dict, Optional
from pathlib import Path
from .config import load_config
from .logging_setup import setup_logging
from .providers.aws.ec2 import EC2Manager
from .providers.aws.s3 import S3Manager
from .providers.aws.iam import IAMManager
from .providers.aws.monitoring import MonitoringManager
from .providers.aws.network import NetworkManager

class InfrastructureManager:
    """Main infrastructure deployment and management class."""
    
    def __init__(self, config_path: Path):
        self.config = load_config(config_path)
        self.logger = setup_logging()
        
        # Initialize providers
        self.ec2 = EC2Manager(self.config)
        self.s3 = S3Manager(self.config)
        self.iam = IAMManager(self.config)
        self.monitoring = MonitoringManager(self.config)
        self.network = NetworkManager(self.config)

    def deploy(self) -> bool:
        """Deploy complete infrastructure."""
        try:
            self.logger.info("Starting infrastructure deployment")
            
            # Create network infrastructure
            vpc_id = self.network.create_vpc()
            subnet_ids = self.network.create_subnets(vpc_id)
            
            # Create IAM roles
            role_arn = self.iam.create_service_role()
            
            # Create S3 bucket
            bucket_name = self.s3.create_bucket()
            
            # Launch EC2 instance
            instance_id = self.ec2.launch_instance(
                subnet_id=subnet_ids[0],
                role_arn=role_arn
            )
            
            # Setup monitoring
            self.monitoring.setup_monitoring(instance_id)
            
            self.logger.info("Infrastructure deployment completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            self.cleanup()
            return False

    def cleanup(self) -> None:
        """Clean up infrastructure resources."""
        try:
            self.logger.info("Starting infrastructure cleanup")
            self.ec2.cleanup()
            self.s3.cleanup()
            self.network.cleanup()
            self.iam.cleanup()
            self.monitoring.cleanup()
            self.logger.info("Cleanup completed successfully")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description="Kaleidoscope Infrastructure Manager")
    parser.add_argument("--config", type=Path, required=True, help="Path to config file")
    parser.add_argument("--action", choices=["deploy", "cleanup"], required=True)
    args = parser.parse_args()

    manager = InfrastructureManager(args.config)
    
    if args.action == "deploy":
        success = manager.deploy()
        exit(0 if success else 1)
    else:
        manager.cleanup()

if __name__ == "__main__":
    main()

# infrastructure/config.py
import yaml
from pathlib import Path
from typing import Dict

def load_config(config_path: Path) -> Dict:
    """Load and validate configuration."""
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    required_fields = [
        "aws_region",
        "environment",
        "vpc_cidr",
        "instance_type",
        "ami_id",
        "bucket_name"
    ]
    
    missing_fields = [field for field in required_fields if field not in config]
    if missing_fields:
        raise ValueError(f"Missing required config fields: {missing_fields}")
    
    return config

# infrastructure/providers/aws/ec2.py
from typing import Dict, Optional
import boto3
from botocore.exceptions import ClientError
import logging

class EC2Manager:
    """Manages EC2 instances and related resources."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.region = config["aws_region"]
        self.ec2 = boto3.client("ec2", region_name=self.region)
        self.logger = logging.getLogger(__name__)

    def launch_instance(self, subnet_id: str, role_arn: str) -> str:
        """Launch EC2 instance with specified configuration."""
        try:
            # Create security group
            sg_id = self._create_security_group()
            
            # Launch instance
            response = self.ec2.run_instances(
                ImageId=self.config["ami_id"],
                InstanceType=self.config["instance_type"],
                SubnetId=subnet_id,
                SecurityGroupIds=[sg_id],
                MinCount=1,
                MaxCount=1,
                IamInstanceProfile={"Arn": role_arn},
                TagSpecifications=[{
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "Name", "Value": f"kaleidoscope-{self.config['environment']}"},
                        {"Key": "Environment", "Value": self.config["environment"]}
                    ]
                }],
                UserData=self._get_user_data()
            )
            
            instance_id = response["Instances"][0]["InstanceId"]
            self.logger.info(f"Launched instance {instance_id}")
            
            # Wait for instance to be running
            self.ec2.get_waiter("instance_running").wait(
                InstanceIds=[instance_id],
                WaiterConfig={"Delay": 10, "MaxAttempts": 30}
            )
            
            return instance_id
            
        except Exception as e:
            self.logger.error(f"Failed to launch instance: {e}")
            raise

    def _create_security_group(self) -> str:
        """Create security group for EC2 instance."""
        try:
            response = self.ec2.create_security_group(
                GroupName=f"kaleidoscope-sg-{self.config['environment']}",
                Description="Kaleidoscope AI security group"
            )
            sg_id = response["GroupId"]
            
            # Configure security group rules
            self.ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 22,
                        "ToPort": 22,
                        "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 443,
                        "ToPort": 443,
                        "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
                    }
                ]
            )
            
            return sg_id
            
        except Exception as e:
            self.logger.error(f"Failed to create security group: {e}")
            raise

    def _get_user_data(self) -> str:
        """Generate user data script for instance initialization."""
        return """#!/bin/bash
# Install required packages
yum update -y
yum install -y amazon-cloudwatch-agent

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c ssm:/kaleidoscope/cloudwatch-agent-config
"""

    def cleanup(self) -> None:
        """Clean up EC2 resources."""
        try:
            # Terminate instances
            instances = self.ec2.describe_instances(
                Filters=[{
                    "Name": "tag:Environment",
                    "Values": [self.config["environment"]]
                }]
            )
            
            for reservation in instances["Reservations"]:
                for instance in reservation["Instances"]:
                    self.ec2.terminate_instances(
                        InstanceIds=[instance["InstanceId"]]
                    )
                    
            # Delete security groups
            sgs = self.ec2.describe_security_groups(
                Filters=[{
                    "Name": "group-name",
                    "Values": [f"kaleidoscope-sg-{self.config['environment']}"]
                }]
            )
            
            for sg in sgs["SecurityGroups"]:
                self.ec2.delete_security_group(GroupId=sg["GroupId"])
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup EC2 resources: {e}")
            raise

# infrastructure/providers/aws/s3.py
class S3Manager:
    """Manages S3 buckets and objects."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.region = config["aws_region"]
        self.s3 = boto3.client("s3", region_name=self.region)
        self.logger = logging.getLogger(__name__)

    def create_bucket(self) -> str:
        """Create and configure S3 bucket."""
        try:
            bucket_name = self.config["bucket_name"]
            
            # Create bucket
            if self.region == "us-east-1":
                self.s3.create_bucket(Bucket=bucket_name)
            else:
                self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        "LocationConstraint": self.region
                    }
                )
            
            # Configure bucket
            self._configure_bucket(bucket_name)
            
            return bucket_name
            
        except Exception as e:
            self.logger.error(f"Failed to create bucket: {e}")
            raise

    def _configure_bucket(self, bucket_name: str) -> None:
        """Configure bucket properties."""
        try:
            # Enable versioning
            self.s3.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={"Status": "Enabled"}
            )
            
            # Enable encryption
            self.s3.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    "Rules": [{
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }]
                }
            )
            
            # Block public access
            self.s3.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    "BlockPublicAcls": True,
                    "IgnorePublicAcls": True,
                    "BlockPublicPolicy": True,
                    "RestrictPublicBuckets": True
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to configure bucket: {e}")
            raise

    def cleanup(self) -> None:
        """Clean up S3 resources."""
        try:
            bucket_name = self.config["bucket_name"]
            
            # Delete all objects and versions
            paginator = self.s3.get_paginator("list_object_versions")
            for page in paginator.paginate(Bucket=bucket_name):
                objects = []
                
                for version in page.get("Versions", []):
                    objects.append({
                        "Key": version["Key"],
                        "VersionId": version["VersionId"]
                    })
                
                if objects:
                    self.s3.delete_objects(
                        Bucket=bucket_name,
                        Delete={"Objects": objects}
                    )
            
            # Delete bucket
            self.s3.delete_bucket(Bucket=bucket_name)
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup S3 resources: {e}")
            raise

# infrastructure/providers/aws/monitoring.py
class MonitoringManager:
    """Manages CloudWatch monitoring and alarms."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.region = config["aws_region"]
        self.cloudwatch = boto3.client("cloudwatch", region_name=self.region)
        self.logger = logging.getLogger(__name__)

    def setup_monitoring(self, instance_id: str) -> None:
        """Set up monitoring for EC2 instance."""
        try:
            # Create CPU utilization alarm
            self.cloudwatch.put_metric_alarm(
                AlarmName=f"kaleidoscope-cpu-{instance_id}",
                ComparisonOperator="GreaterThanThreshold",
                EvaluationPeriods=2,
                MetricName="CPUUtilization",
                Namespace="AWS/EC2",
                Period=300,
                Statistic="Average",
                Threshold=80.0,
                ActionsEnabled=True,
                AlarmDescription="CPU utilization is too high",
                Dimensions=[{
                    "Name": "InstanceId",
                    "Value": instance_id
                }]
            )
            
            # Create memory utilization alarm
            self.cloudwatch.put_metric_alarm(
                AlarmName=f"kaleidoscope-memory-{instance_id}",
                ComparisonOperator="GreaterThanThreshold",
                EvaluationPeriods=2,
                MetricName="MemoryUtilization",
                Namespace="CWAgent",
                Period=300,
                Statistic="Average",
                Threshold=80.0,
                ActionsEnabled=True,
                AlarmDescription="Memory utilization is too high",
                Dimensions=[{
                    "Name": "InstanceId",
                    "Value": instance_id
                }]
            )
            
        except Exception as e:
            self.logger.error(f"Failed to setup monitoring: {e}")
            raise

    def cleanup(self) -> None:
        """Clean up CloudWatch resources."""
        try:
            # Delete alarms
            alarms = self.cloudwatch.describe_alarms(
                AlarmNamePrefix="kaleidoscope"
            )
            
            alarm_names = [alarm["AlarmName"] for alarm in alarms["MetricAlarms"]]
            if alarm_names:
                self.cloudwatch.delete_alarms(AlarmNames=alarm_names)
                
            self.logger.info("Cleaned up CloudWatch resources")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup CloudWatch resources: {e}")
            raise

# infrastructure/providers/aws/network.py
class NetworkManager:
    """Manages VPC and networking resources."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.region = config["aws_region"]
        self.ec2 = boto3.client("ec2", region_name=self.region)
        self.logger = logging.getLogger(__name__)

    def create_vpc(self) -> str:
        """Create VPC with required configuration."""
        try:
            # Create VPC
            response = self.ec2.create_vpc(
                CidrBlock=self.config["vpc_cidr"],
                TagSpecifications=[{
                    'ResourceType': 'vpc',
                    'Tags': [
                        {'Key': 'Name', 'Value': f'kaleidoscope-vpc-{self.config["environment"]}'},
                        {'Key': 'Environment', 'Value': self.config["environment"]}
                    ]
                }]
            )
            vpc_id = response['Vpc']['VpcId']

            # Enable DNS hostnames
            self.ec2.modify_vpc_attribute(
                VpcId=vpc_id,
                EnableDnsHostnames={'Value': True}
            )

            # Enable DNS support
            self.ec2.modify_vpc_attribute(
                VpcId=vpc_id,
                EnableDnsSupport={'Value': True}
            )

            # Create Internet Gateway
            igw_response = self.ec2.create_internet_gateway()
            igw_id = igw_response['InternetGateway']['InternetGatewayId']
            
            # Attach Internet Gateway to VPC
            self.ec2.attach_internet_gateway(
                InternetGatewayId=igw_id,
                VpcId=vpc_id
            )

            self.logger.info(f"Created VPC {vpc_id} with Internet Gateway {igw_id}")
            return vpc_id

        except Exception as e:
            self.logger.error(f"Failed to create VPC: {e}")
            raise

    def create_subnets(self, vpc_id: str) -> List[str]:
        """Create subnets in the VPC."""
        try:
            subnet_ids = []
            azs = self.ec2.describe_availability_zones()['AvailabilityZones']
            
            # Create public subnet in each AZ
            for i, az in enumerate(azs[:2]):  # Create in first 2 AZs
                cidr_block = f"10.0.{i}.0/24"  # Assuming VPC CIDR is 10.0.0.0/16
                
                response = self.ec2.create_subnet(
                    VpcId=vpc_id,
                    CidrBlock=cidr_block,
                    AvailabilityZone=az['ZoneName'],
                    TagSpecifications=[{
                        'ResourceType': 'subnet',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'kaleidoscope-subnet-{i}'},
                            {'Key': 'Environment', 'Value': self.config["environment"]}
                        ]
                    }]
                )
                subnet_id = response['Subnet']['SubnetId']
                subnet_ids.append(subnet_id)

                # Enable auto-assign public IP
                self.ec2.modify_subnet_attribute(
                    SubnetId=subnet_id,
                    MapPublicIpOnLaunch={'Value': True}
                )

            # Create and configure route table
            route_table = self.ec2.create_route_table(VpcId=vpc_id)
            rt_id = route_table['RouteTable']['RouteTableId']

            # Add route to Internet Gateway
            self.ec2.create_route(
                RouteTableId=rt_id,
                DestinationCidrBlock='0.0.0.0/0',
                GatewayId=igw_id
            )

            # Associate route table with subnets
            for subnet_id in subnet_ids:
                self.ec2.associate_route_table(
                    RouteTableId=rt_id,
                    SubnetId=subnet_id
                )

            self.logger.info(f"Created {len(subnet_ids)} subnets in VPC {vpc_id}")
            return subnet_ids

        except Exception as e:
            self.logger.error(f"Failed to create subnets: {e}")
            raise

    def cleanup(self) -> None:
        """Clean up networking resources."""
        try:
            # Get VPC ID
            vpcs = self.ec2.describe_vpcs(
                Filters=[{
                    'Name': 'tag:Environment',
                    'Values': [self.config["environment"]]
                }]
            )

            for vpc in vpcs['Vpcs']:
                vpc_id = vpc['VpcId']

                # Delete subnets
                subnets = self.ec2.describe_subnets(
                    Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
                )
                for subnet in subnets['Subnets']:
                    self.ec2.delete_subnet(SubnetId=subnet['SubnetId'])

                # Delete route tables
                route_tables = self.ec2.describe_route_tables(
                    Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
                )
                for rt in route_tables['RouteTables']:
                    if not rt.get('Associations', []):  # Skip main route table
                        self.ec2.delete_route_table(RouteTableId=rt['RouteTableId'])

                # Detach and delete Internet Gateway
                igws = self.ec2.describe_internet_gateways(
                    Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}]
                )
                for igw in igws['InternetGateways']:
                    self.ec2.detach_internet_gateway(
                        InternetGatewayId=igw['InternetGatewayId'],
                        VpcId=vpc_id
                    )
                    self.ec2.delete_internet_gateway(
                        InternetGatewayId=igw['InternetGatewayId']
                    )

                # Delete VPC
                self.ec2.delete_vpc(VpcId=vpc_id)

            self.logger.info("Cleaned up networking resources")

        except Exception as e:
            self.logger.error(f"Failed to cleanup networking resources: {e}")
            raise

# infrastructure/providers/aws/iam.py
class IAMManager:
    """Manages IAM roles and policies."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.region = config["aws_region"]
        self.iam = boto3.client("iam")
        self.logger = logging.getLogger(__name__)

    def create_service_role(self) -> str:
        """Create service role for EC2 instances."""
        try:
            role_name = f"kaleidoscope-role-{self.config['environment']}"

            # Create role
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }]
            }

            response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Kaleidoscope AI service role"
            )

            role_arn = response['Role']['Arn']

            # Attach required policies
            required_policies = [
                "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
                "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
            ]

            for policy_arn in required_policies:
                self.iam.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )

            # Create instance profile
            self.iam.create_instance_profile(
                InstanceProfileName=role_name
            )

            # Add role to instance profile
            self.iam.add_role_to_instance_profile(
                InstanceProfileName=role_name,
                RoleName=role_name
            )

            self.logger.info(f"Created service role {role_name}")
            return role_arn

        except Exception as e:
            self.logger.error(f"Failed to create service role: {e}")
            raise

    def cleanup(self) -> None:
        """Clean up IAM resources."""
        try:
            role_name = f"kaleidoscope-role-{self.config['environment']}"

            # Remove role from instance profile
            try:
                self.iam.remove_role_from_instance_profile(
                    InstanceProfileName=role_name,
                    RoleName=role_name
                )
            except self.iam.exceptions.NoSuchEntityException:
                pass

            # Delete instance profile
            try:
                self.iam.delete_instance_profile(
                    InstanceProfileName=role_name
                )
            except self.iam.exceptions.NoSuchEntityException:
                pass

            # Detach policies
            attached_policies = self.iam.list_attached_role_policies(
                RoleName=role_name
            )['AttachedPolicies']

            for policy in attached_policies:
                self.iam.detach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy['PolicyArn']
                )

            # Delete role
            try:
                self.iam.delete_role(RoleName=role_name)
            except self.iam.exceptions.NoSuchEntityException:
                pass

            self.logger.info(f"Cleaned up IAM resources for {role_name}")

        except Exception as e:
            self.logger.error(f"Failed to cleanup IAM resources: {e}")
            raise

# config/config.yaml
aws_region: us-east-1
environment: production
vpc_cidr: 10.0.0.0/16

instance_type: t3.medium
ami_id: ami-0123456789abcdef0  # Amazon Linux 2 AMI ID
key_name: kaleidoscope-key

bucket_name: kaleidoscope-ai-data

tags:
  Environment: production
  Service: KaleidoscopeAI
  Owner: DataScience

monitoring:
  metrics_namespace: KaleidoscopeAI
  log_retention_days: 30
  alarms:
    cpu_threshold: 80
    memory_threshold: 80
    disk_threshold: 85

# config/logging.yaml
version: 1
formatters:
  standard:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: standard
    level: INFO
    stream: ext://sys.stdout
  file:
    class: logging.FileHandler
    formatter: standard
    level: DEBUG
    filename: kaleidoscope.log
loggers:
  infrastructure:
    level: DEBUG
    handlers: [console, file]
    propagate: no
root:
  level: INFO
  handlers: [console]
  # tests/conftest.py
import pytest
import boto3
import os
from moto import mock_ec2, mock_s3, mock_iam, mock_cloudwatch
from pathlib import Path
from typing import Dict

@pytest.fixture
def aws_credentials():
    """Mock AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture
def test_config() -> Dict:
    """Test configuration."""
    return {
        'aws_region': 'us-east-1',
        'environment': 'test',
        'vpc_cidr': '10.0.0.0/16',
        'instance_type': 't3.medium',
        'ami_id': 'ami-12345678',
        'key_name': 'test-key',
        'bucket_name': '
        # tests/conftest.py
import pytest
import boto3
import os
from moto import mock_ec2, mock_s3, mock_iam, mock_cloudwatch
from pathlib import Path
from typing import Dict

@pytest.fixture
def aws_credentials():
    """Mock AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture
def test_config() -> Dict:
    """Test configuration."""
    return {
        'aws_region': 'us-east-1',
        'environment': 'test',
        'vpc_cidr': '10.0.0.0/16',
        'instance_type': 't3.medium',
        'ami_id': 'ami-12345678',
        'key_name': 'test-key',
        'bucket_name': 'test-kaleidoscope-bucket',
        'monitoring': {
            'metrics_namespace': 'KaleidoscopeTest',
            'log_retention_days': 7,
            'alarms': {
                'cpu_threshold': 80,
                'memory_threshold': 80,
                'disk_threshold': 85
            }
        },
        'tags': {
            'Environment': 'test',
            'Service': 'KaleidoscopeAI'
        }
    }

# tests/test_infrastructure.py
import pytest
from moto import mock_ec2, mock_s3, mock_iam, mock_cloudwatch
from infrastructure.providers.aws.ec2 import EC2Manager
from infrastructure.providers.aws.s3 import S3Manager
from infrastructure.providers.aws.iam import IAMManager
from infrastructure.providers.aws.monitoring import MonitoringManager
from infrastructure.providers.aws.network import NetworkManager

class TestNetworkManager:
    """Test networking functionality."""

    @mock_ec2
    def test_create_vpc(self, test_config, aws_credentials):
        """Test VPC creation with proper configuration."""
        network_manager = NetworkManager(test_config)
        vpc_id = network_manager.create_vpc()

        # Verify VPC exists
        ec2 = boto3.client('ec2', region_name=test_config['aws_region'])
        vpc = ec2.describe_vpcs(VpcIds=[vpc_id])['Vpcs'][0]
        
        assert vpc['CidrBlock'] == test_config['vpc_cidr']
        assert vpc['State'] == 'available'

    @mock_ec2
    def test_create_subnets(self, test_config, aws_credentials):
        """Test subnet creation in VPC."""
        network_manager = NetworkManager(test_config)
        vpc_id = network_manager.create_vpc()
        subnet_ids = network_manager.create_subnets(vpc_id)

        # Verify subnets exist
        ec2 = boto3.client('ec2', region_name=test_config['aws_region'])
        subnets = ec2.describe_subnets(SubnetIds=subnet_ids)['Subnets']
        
        assert len(subnets) == 2  # We create 2 subnets
        for subnet in subnets:
            assert subnet['VpcId'] == vpc_id
            assert subnet['State'] == 'available'

class TestEC2Manager:
    """Test EC2 instance management."""

    @mock_ec2
    @mock_iam
    def test_launch_instance(self, test_config, aws_credentials):
        """Test EC2 instance launch with proper configuration."""
        # Set up dependencies
        network_manager = NetworkManager(test_config)
        vpc_id = network_manager.create_vpc()
        subnet_ids = network_manager.create_subnets(vpc_id)
        
        iam_manager = IAMManager(test_config)
        role_arn = iam_manager.create_service_role()

        # Launch instance
        ec2_manager = EC2Manager(test_config)
        instance_id = ec2_manager.launch_instance(subnet_ids[0], role_arn)

        # Verify instance
        ec2 = boto3.client('ec2', region_name=test_config['aws_region'])
        instance = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
        
        assert instance['InstanceType'] == test_config['instance_type']
        assert instance['State']['Name'] == 'running'
        assert instance['SubnetId'] == subnet_ids[0]

class TestS3Manager:
    """Test S3 bucket management."""

    @mock_s3
    def test_create_bucket(self, test_config, aws_credentials):
        """Test S3 bucket creation and configuration."""
        s3_manager = S3Manager(test_config)
        bucket_name = s3_manager.create_bucket()

        # Verify bucket exists and configuration
        s3 = boto3.client('s3', region_name=test_config['aws_region'])
        
        # Check bucket exists
        buckets = s3.list_buckets()['Buckets']
        assert any(b['Name'] == bucket_name for b in buckets)

        # Check versioning
        versioning = s3.get_bucket_versioning(Bucket=bucket_name)
        assert versioning.get('Status') == 'Enabled'

        # Check encryption
        encryption = s3.get_bucket_encryption(Bucket=bucket_name)
        assert encryption['ServerSideEncryptionConfiguration']['Rules'][0]['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] == 'AES256'

class TestMonitoringManager:
    """Test CloudWatch monitoring setup."""

    @mock_cloudwatch
    @mock_ec2
    def test_setup_monitoring(self, test_config, aws_credentials):
        """Test CloudWatch alarms and metrics configuration."""
        # Set up EC2 instance
        ec2 = boto3.client('ec2', region_name=test_config['aws_region'])
        instance = ec2.run_instances(
            ImageId=test_config['ami_id'],
            InstanceType=test_config['instance_type'],
            MinCount=1,
            MaxCount=1
        )['Instances'][0]

        # Setup monitoring
        monitoring_manager = MonitoringManager(test_config)
        monitoring_manager.setup_monitoring(instance['InstanceId'])

        # Verify alarms
        cloudwatch = boto3.client('cloudwatch', region_name=test_config['aws_region'])
        alarms = cloudwatch.describe_alarms()['MetricAlarms']
        
        assert any(a['Namespace'] == 'AWS/EC2' for a in alarms)
        assert any(a['MetricName'] == 'CPUUtilization' for a in alarms)
        assert any(a['MetricName'] == 'MemoryUtilization' for a in alarms)

class TestIAMManager:
    """Test IAM role and policy management."""

    @mock_iam
    def test_create_service_role(self, test_config, aws_credentials):
        """Test IAM role creation with proper policies."""
        iam_manager = IAMManager(test_config)
        role_arn = iam_manager.create_service_role()

        # Verify role and policies
        iam = boto3.client('iam')
        role_name = f"kaleidoscope-role-{test_config['environment']}"
        
        # Check role exists
        role = iam.get_role(RoleName=role_name)['Role']
        assert role['Arn'] == role_arn

        # Check policies
        attached_policies = iam.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
        policy_names = [p['PolicyName'] for p in attached_policies]
        
        assert 'AmazonS3ReadOnlyAccess' in policy_names
        assert 'CloudWatchAgentServerPolicy' in policy_names

# tests/test_integration.py
import pytest
from infrastructure.main import InfrastructureManager

@pytest.mark.integration
class TestInfrastructureIntegration:
    """Integration tests for complete infrastructure deployment."""

    @mock_ec2
    @mock_s3
    @mock_iam
    @mock_cloudwatch
    def test_complete_deployment(self, test_config, aws_credentials):
        """Test complete infrastructure deployment process."""
        manager = InfrastructureManager(test_config)
        success = manager.deploy()

        assert success

        # Verify all resources
        ec2 = boto3.client('ec2', region_name=test_config['aws_region'])
        s3 = boto3.client('s3', region_name=test_config['aws_region'])
        iam = boto3.client('iam')
        cloudwatch = boto3.client('cloudwatch', region_name=test_config['aws_region'])

        # Check VPC
        vpcs = ec2.describe_vpcs(
            Filters=[{
                'Name': 'tag:Environment',
                'Values': [test_config['environment']]
            }]
        )['Vpcs']
        assert len(vpcs) == 1

        # Check EC2 instance
        instances = ec2.describe_instances(
            Filters=[{
                'Name': 'tag:Environment',
                'Values': [test_config['environment']]
            }]
        )['Reservations'][0]['Instances']
        assert len(instances) == 1
        assert instances[0]['State']['Name'] == 'running'

        # Check S3 bucket
        buckets = s3.list_buckets()['Buckets']
        assert any(b['Name'] == test_config['bucket_name'] for b in buckets)

        # Check IAM role
        role_name = f"kaleidoscope-role-{test_config['environment']}"
        role = iam.get_role(RoleName=role_name)['Role']
        assert role['RoleName'] == role_name

        # Check CloudWatch alarms
        alarms = cloudwatch.describe_alarms()['MetricAlarms']
        assert len(alarms) >= 2  # CPU and Memory alarms

    def test_cleanup(self, test_config, aws_credentials):
        """Test complete infrastructure cleanup process."""
        manager = InfrastructureManager(test_config)
        manager.cleanup()

        # Verify all resources are cleaned up
        ec2 = boto3.client('ec2', region_name=test_config['aws_region'])
        s3 = boto3.client('s3', region_name=test_config['aws_region'])
        
        # Check VPC is deleted
        vpcs = ec2.describe_vpcs(
            Filters=[{
                'Name': 'tag:Environment',
                'Values': [test_config['environment']]
            }]
        )['Vpcs']
        assert len(vpcs) == 0

        # Check S3 bucket is deleted
        buckets = s3.list_buckets()['Buckets']
        assert not any(b['Name'] == test_config['bucket_name'] for b in buckets)

# requirements.txt
boto3>=1.26.0
botocore>=1.29.0
pyyaml>=6.0
moto>=4.1.0
pytest>=7.3.0
pytest-asyncio>=0.21.0
typing-extensions>=4.5.0
python-json-logger>=2.0.7
pip install boto3 botocore moto pyyaml pytest pytest-asyncio typing-extensions python-json-logger
# infrastructure/utils/backup_manager.py
import boto3
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

class BackupManager:
    """Manages AWS Backup for infrastructure resources."""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.backup = boto3.client('backup', region_name=config['aws_region'])
        self.iam = boto3.client('iam', region_name=config['aws_region'])

    def setup_backup_vault(self) -> str:
        """Create and configure backup vault."""
        try:
            vault_name = f"kaleidoscope-{self.config['environment']}-vault"
            
            # Create backup vault
            response = self.backup.create_backup_vault(
                BackupVaultName=vault_name,
                Tags={
                    'Environment': self.config['environment'],
                    'Service': 'KaleidoscopeAI'
                }
            )
            
            # Configure encryption if specified
            if self.config.get('backup', {}).get('encryption_key'):
                self.backup.put_backup_vault_access_policy(
                    BackupVaultName=vault_name,
                    Policy=self._generate_vault_policy()
                )
            
            return response['BackupVaultArn']
