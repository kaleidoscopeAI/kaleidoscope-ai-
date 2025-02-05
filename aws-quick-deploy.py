#!/usr/bin/env python3
import os
import boto3
import configparser
from pathlib import Path
import sys

class AWSConfigurer:
    def __init__(self):
        self.credentials_path = Path.home() / '.aws' / 'credentials'
        self.config_path = Path.home() / '.aws' / 'config'
        
    def setup_credentials(self, access_key: str, secret_key: str, region: str = 'us-east-1'):
        # Create .aws directory if it doesn't exist
        self.credentials_path.parent.mkdir(exist_ok=True)
        
        # Write credentials file
        credentials = configparser.ConfigParser()
        credentials['default'] = {
            'aws_access_key_id': access_key,
            'aws_secret_access_key': secret_key
        }
        
        with open(self.credentials_path, 'w') as f:
            credentials.write(f)
        
        # Secure the credentials file
        os.chmod(self.credentials_path, 0o600)
        
        # Write config file
        config = configparser.ConfigParser()
        config['default'] = {
            'region': region,
            'output': 'json'
        }
        
        with open(self.config_path, 'w') as f:
            config.write(f)
            
        return self.verify_credentials()
        
    def verify_credentials(self) -> bool:
        try:
            session = boto3.Session()
            sts = session.client('sts')
            sts.get_caller_identity()
            return True
        except Exception as e:
            print(f"Failed to verify credentials: {e}")
            return False

def main():
    # Replace with your actual keys from '872515289083 Account details.txt'
    ACCESS_KEY = 'AKIA4WJPWX75SNC5OJWQ'  # Your access key ID
    SECRET_KEY = input("Enter your AWS Secret Access Key: ").strip()
    
    configurer = AWSConfigurer()
    if configurer.setup_credentials(ACCESS_KEY, SECRET_KEY):
        print("AWS credentials configured successfully")
        print("You can now run the deployment scripts")
        sys.exit(0)
    else:
        print("Failed to configure AWS credentials")
        sys.exit(1)

if __name__ == "__main__":
    main()
