#!/usr/bin/env python3
"""
Kaleidoscope AI Infrastructure Deployment Script
---------------------------------------------
Deploys or cleans up Kaleidoscope AI infrastructure in AWS.
"""

import argparse
import logging
import sys
import json
import boto3
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from botocore.exceptions import ClientError
from infrastructure.main import InfrastructureManager
from infrastructure.config import load_config

class DeploymentValidator:
    """Validates AWS credentials and permissions before deployment."""
    
    def __init__(self, region: str):
        self.region = region
        self.sts = boto3.client('sts', region_name=region)
        self.iam = boto3.client('iam', region_name=region)
    
    def validate_aws_credentials(self) -> Dict:
        """Validate AWS credentials and return account info."""
        try:
            response = self.sts.get_caller_identity()
            return {
                'account_id': response['Account'],
                'arn': response['Arn'],
                'user_id': response['UserId']
            }
        except Exception as e:
            raise ValueError(f"Invalid AWS credentials: {str(e)}")

    def check_required_permissions(self) -> Dict[str, bool]:
        """Check if current credentials have required permissions."""
        required_actions = {
            'ec2': [
                'ec2:CreateVpc',
                'ec2:CreateSubnet',
                'ec2:CreateSecurityGroup',
                'ec2:RunInstances',
                'ec2:DescribeInstances'
            ],
            's3': [
                's3:CreateBucket',
                's3:PutObject',
                's3:PutBucketPolicy'
            ],
            'iam': [
                'iam:CreateRole',
                'iam:PutRolePolicy',
                'iam:AttachRolePolicy'
            ],
            'cloudwatch': [
                'cloudwatch:PutMetricAlarm',
                'cloudwatch:PutDashboard'
            ]
        }

        permissions_status = {}
        
        try:
            for service, actions in required_actions.items():
                policy_document = {
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Action": actions,
                        "Resource": "*"
                    }]
                }
                
                try:
                    self.iam.simulate_custom_policy(
                        PolicyInputList=[json.dumps(policy_document)],
                        ActionNames=actions
                    )
                    permissions_status[service] = True
                except ClientError:
                    permissions_status[service] = False
                    
        except Exception as e:
            raise ValueError(f"Failed to check permissions: {str(e)}")
            
        return permissions_status

def setup_logging(verbose: bool = False, log_dir: Optional[Path] = None) -> logging.Logger:
    """Configure logging for deployment script."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory if specified
    if log_dir:
        log_dir.mkdir(exist_ok=True)
    else:
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logger = logging.getLogger('deployment')
    logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler with colored output
    class ColoredFormatter(logging.Formatter):
        """Formatter that adds colors to log levels."""
        
        COLORS = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[41m', # Red background
        }
        RESET = '\033[0m'
        
        def format(self, record):
            color = self.COLORS.get(record.levelname, '')
            record.levelname_colored = f"{color}{record.levelname}{self.RESET}"
            return super().format(record)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = ColoredFormatter('%(asctime)s - %(levelname_colored)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_handler = logging.FileHandler(log_dir / f'deployment_{timestamp}.log')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

def validate_config(config: Dict, logger: logging.Logger) -> bool:
    """Validate configuration values."""
    required_fields = {
        'aws_region': str,
        'environment': str,
        'vpc_cidr': str,
        'instance_type': str,
        'ami_id': str,
        'bucket_name': str,
        'monitoring': dict
    }
    
    # Check required fields and types
    for field, expected_type in required_fields.items():
        if field not in config:
            logger.error(f"Missing required configuration field: {field}")
            return False
        if not isinstance(config[field], expected_type):
            logger.error(
                f"Invalid type for {field}. Expected {expected_type}, "
                f"got {type(config[field])}"
            )
            return False
    
    # Validate specific values
    if not config['vpc_cidr'].endswith('/16'):
        logger.error("VPC CIDR must be a /16 network")
        return False
        
    if not config['bucket_name'].isalnum():
        logger.error("Bucket name must be alphanumeric")
        return False
    
    return True

def display_deployment_summary(config: Dict, logger: logging.Logger) -> None:
    """Display summary of resources to be deployed."""
    logger.info("Deployment Summary:")
    logger.info("===================")
    logger.info(f"Environment: {config['environment']}")
    logger.info(f"Region: {config['aws_region']}")
    logger.info(f"VPC CIDR: {config['vpc_cidr']}")
    logger.info(f"Instance Type: {config['instance_type']}")
    logger.info(f"S3 Bucket: {config['bucket_name']}")
    logger.info("===================")

def cleanup_resources(manager: InfrastructureManager, logger: logging.Logger) -> bool:
    """Clean up infrastructure resources with proper error handling."""
    try:
        logger.info("Starting resource cleanup")
        
        # Track cleanup progress
        resources_cleaned = {
            'ec2': False,
            's3': False,
            'cloudwatch': False,
            'iam': False,
            'vpc': False
        }
        
        # Clean up EC2 instances first
        try:
            manager.ec2.cleanup()
            resources_cleaned['ec2'] = True
            logger.info("EC2 resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Failed to clean up EC2 resources: {e}")
        
        # Clean up S3 buckets
        try:
            manager.s3.cleanup()
            resources_cleaned['s3'] = True
            logger.info("S3 resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Failed to clean up S3 resources: {e}")
        
        # Clean up CloudWatch resources
        try:
            manager.monitoring.cleanup()
            resources_cleaned['cloudwatch'] = True
            logger.info("CloudWatch resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Failed to clean up CloudWatch resources: {e}")
        
        # Clean up IAM roles and policies
        try:
            manager.iam.cleanup()
            resources_cleaned['iam'] = True
            logger.info("IAM resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Failed to clean up IAM resources: {e}")
        
        # Clean up VPC and networking last
        try:
            manager.network.cleanup()
            resources_cleaned['vpc'] = True
            logger.info("VPC resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Failed to clean up VPC resources: {e}")
        
        # Return True only if all resources were cleaned up
        return all(resources_cleaned.values())
        
    except Exception as e:
        logger.error(f"Cleanup failed with unexpected error: {e}")
        return False

def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(
        description='Deploy Kaleidoscope AI Infrastructure',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'action',
        choices=['deploy', 'cleanup'],
        help='Action to perform'
    )
    parser.add_argument(
        '--config',
        type=Path,
        required=True,
        help='Path to configuration YAML file'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force cleanup without confirmation'
    )
    parser.add_argument(
        '--log-dir',
        type=Path,
        help='Directory for log files'
    )
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.verbose, args.log_dir)
    
    try:
        # Load and validate configuration
        logger.info(f"Loading configuration from {args.config}")
        config = load_config(args.config)
        
        if not validate_config(config, logger):
            logger.error("Configuration validation failed")
            sys.exit(1)
        
        # Validate AWS credentials and permissions
        validator = DeploymentValidator(config['aws_region'])
        
        try:
            account_info = validator.validate_aws_credentials()
            logger.info(f"Using AWS Account: {account_info['account_id']}")
            
            permissions = validator.check_required_permissions()
            missing_permissions = [
                service for service, has_permission in permissions.items()
                if not has_permission
            ]
            
            if missing_permissions:
                logger.error(
                    f"Missing required permissions for services: "
                    f"{', '.join(missing_permissions)}"
                )
                sys.exit(1)
                
        except ValueError as e:
            logger.error(f"AWS validation failed: {e}")
            sys.exit(1)
        
        # Initialize infrastructure manager
        manager = InfrastructureManager(config)
        
        if args.action == 'deploy':
            # Show deployment summary
            display_deployment_summary(config, logger)
            
            # Confirm deployment
            if not args.force:
                confirm = input(
                    f"Do you want to proceed with deployment to "
                    f"{config['environment']}? [y/N] "
                )
                if confirm.lower() != 'y':
                    logger.info("Deployment cancelled")
                    sys.exit(0)
            
            logger.info("Starting infrastructure deployment")
            start_time = time.time()
            
            success = manager.deploy()
            
            end_time = time.time()
            duration = end_time - start_time
            
            if success:
                logger.info(
                    f"Infrastructure deployment completed successfully "
                    f"in {duration:.2f} seconds"
                )
                sys.exit(0)
            else:
                logger.error("Infrastructure deployment failed")
                sys.exit(1)
                
        elif args.action == 'cleanup':
            if not args.force:
                confirm = input(
                    f"Are you sure you want to cleanup the "
                    f"{config['environment']} environment? This action "
                    f"cannot be undone! [y/N] "
                )
                if confirm.lower() != 'y':
                    logger.info("Cleanup cancelled")
                    sys.exit(0)
            
            success = cleanup_resources(manager, logger)
            
            if success:
                logger.info("Infrastructure cleanup completed successfully")
                sys.exit(0)
            else:
                logger.error(
                    "Infrastructure cleanup completed with some failures. "
                    "Check logs for details."
                )
                sys.exit(1)
            
    except Exception as e:
        logger.error(f"Deployment script failed: {str(e)}")
        if args.verbose:
            logger.exception("Detailed error traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()
