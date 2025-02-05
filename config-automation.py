# config_manager.py
import yaml
import json
import os
import boto3
from typing import Dict, Optional, List
from dataclasses import dataclass
from pathlib import Path

@dataclass
class AWSConfig:
    """AWS-specific configuration parameters."""
    account_id: str
    region: str
    vpc_cidr: str = "10.0.0.0/16"
    subnet_cidrs: List[str] = None
    availability_zones: List[str] = None

@dataclass
class ResourceConfig:
    """Resource-specific configuration parameters."""
    stack_name: str
    environment: str
    instance_types: Dict[str, str]
    memory_sizes: Dict[str, int]
    storage_config: Dict[str, Dict]

class ConfigurationManager:
    """Manages system configuration and template generation."""
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = Path(template_dir)
        self.aws_config: Optional[AWSConfig] = None
        self.resource_config: Optional[ResourceConfig] = None
        
    def generate_template(self, output_path: str) -> None:
        """Generate configuration template with placeholders."""
        template = {
            "aws": {
                "account_id": "YOUR_ACCOUNT_ID",
                "region": "us-east-1",
                "vpc": {
                    "cidr": "10.0.0.0/16",
                    "subnets": ["10.0.1.0/24", "10.0.2.0/24"],
                    "availability_zones": ["us-east-1a", "us-east-1b"]
                }
            },
            "stack": {
                "name": "quantum-system",
                "environment": "Production",
                "tags": {
                    "Project": "QuantumNodes",
                    "Owner": "YOUR_TEAM"
                }
            },
            "resources": {
                "compute": {
                    "sagemaker_instance": "ml.p3.2xlarge",
                    "lambda_memory": 3008,
                    "elasticache_instance": "cache.r6g.xlarge",
                    "elasticache_nodes": 2
                },
                "storage": {
                    "s3": {
                        "versioning": True,
                        "encryption": True,
                        "lifecycle_rules": {
                            "transition_days": 90,
                            "storage_class": "INTELLIGENT_TIERING"
                        }
                    },
                    "dynamodb": {
                        "billing_mode": "PAY_PER_REQUEST",
                        "point_in_time_recovery": True
                    }
                },
                "monitoring": {
                    "metrics_resolution": 60,
                    "alert_endpoints": ["YOUR_EMAIL@domain.com"],
                    "thresholds": {
                        "cpu_utilization": 80,
                        "memory_utilization": 75,
                        "error_rate": 1
                    }
                }
            }
        }
        
        with open(output_path, 'w') as f:
            yaml.safe_dump(template, f, default_flow_style=False)
            
    def load_configuration(self, config_path: str) -> None:
        """Load and validate configuration from file."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        self._validate_configuration(config)
        
        # Create AWS configuration
        self.aws_config = AWSConfig(
            account_id=config['aws']['account_id'],
            region=config['aws']['region'],
            vpc_cidr=config['aws']['vpc']['cidr'],
            subnet_cidrs=config['aws']['vpc']['subnets'],
            availability_zones=config['aws']['vpc']['availability_zones']
        )
        
        # Create resource configuration
        self.resource_config = ResourceConfig(
            stack_name=config['stack']['name'],
            environment=config['stack']['environment'],
            instance_types={
                'sagemaker': config['resources']['compute']['sagemaker_instance'],
                'elasticache': config['resources']['compute']['elasticache_instance']
            },
            memory_sizes={
                'lambda': config['resources']['compute']['lambda_memory']
            },
            storage_config=config['resources']['storage']
        )

    def _validate_configuration(self, config: Dict) -> None:
        """Validate configuration structure and values."""
        required_sections = ['aws', 'stack', 'resources']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required section: {section}")
                
        # Validate AWS configuration
        if not config['aws'].get('account_id'):
            raise ValueError("AWS Account ID is required")
            
        # Validate CIDR ranges
        vpc_cidr = config['aws']['vpc']['cidr']
        if not self._is_valid_cidr(vpc_cidr):
            raise ValueError(f"Invalid VPC CIDR: {vpc_cidr}")

    def _is_valid_cidr(self, cidr: str) -> bool:
        """Validate CIDR block format."""
        try:
            network, bits = cidr.split('/')
            octets = network.split('.')
            return len(octets) == 4 and all(0 <= int(octet) <= 255 for octet in octets)
        except:
            return False

    def generate_cloudformation(self) -> str:
        """Generate CloudFormation template from configuration."""
        if not self.aws_config or not self.resource_config:
            raise ValueError("Configuration must be loaded first")
            
        template_path = self.template_dir / "cloudformation.yaml"
        with open(template_path, 'r') as f:
            cf_template = f.read()
            
        # Replace placeholders with actual values
        cf_template = cf_template.replace("${AWS::AccountId}", self.aws_config.account_id)
        cf_template = cf_template.replace("${AWS::Region}", self.aws_config.region)
        cf_template = cf_template.replace("${StackName}", self.resource_config.stack_name)
        
        return cf_template

    def deploy_configuration(self) -> None:
        """Deploy the configuration to AWS."""
        if not self.aws_config or not self.resource_config:
            raise ValueError("Configuration must be loaded first")
            
        # Generate CloudFormation template
        cf_template = self.generate_cloudformation()
        
        # Deploy using AWS CloudFormation
        cf_client = boto3.client('cloudformation', region_name=self.aws_config.region)
        cf_client.create_stack(
            StackName=self.resource_config.stack_name,
            TemplateBody=cf_template,
            Capabilities=['CAPABILITY_NAMED_IAM'],
            Parameters=[
                {
                    'ParameterKey': 'Environment',
                    'ParameterValue': self.resource_config.environment
                }
            ]
        )

def setup_system():
    """Main function to set up the system."""
    config_manager = ConfigurationManager()
    
    # Generate template if it doesn't exist
    if not os.path.exists('config.yaml'):
        config_manager.generate_template('config.yaml')
        print("Configuration template generated as 'config.yaml'")
        print("Please fill in the required values and run the script again")
        return
        
    # Load and validate configuration
    try:
        config_manager.load_configuration('config.yaml')
        print("Configuration loaded successfully")
        
        # Deploy the system
        config_manager.deploy_configuration()
        print("System deployment initiated")
        
    except Exception as e:
        print(f"Error during setup: {str(e)}")

if __name__ == "__main__":
    setup_system()
