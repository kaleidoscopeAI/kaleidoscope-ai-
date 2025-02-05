#!/usr/bin/env python3
import boto3
import os
import sys
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor
import logging

class AWSDeployer:
    def __init__(self):
        self.session = boto3.Session()
        self.s3 = self.session.client('s3')
        self.sagemaker = self.session.client('sagemaker')
        self.account_id = self.session.client('sts').get_caller_identity()['Account']
        self.region = self.session.region_name
        self.bucket = f'kaleidoscope-{self.account_id}-{self.region}'

    def ensure_bucket(self):
        try:
            if self.region == 'us-east-1':
                self.s3.create_bucket(Bucket=self.bucket)
            else:
                self.s3.create_bucket(
                    Bucket=self.bucket,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
        except self.s3.exceptions.BucketAlreadyExists:
            pass
        
    def upload_directory(self, local_dir: str, s3_prefix: str = ''):
        local_path = Path(local_dir)
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for file_path in local_path.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(local_path)
                    s3_key = f"{s3_prefix}/{relative_path}"
                    futures.append(
                        executor.submit(
                            self.s3.upload_file,
                            str(file_path),
                            self.bucket,
                            s3_key
                        )
                    )
            for future in futures:
                future.result()

    def deploy(self, script_dir: str = '.'):
        self.ensure_bucket()
        self.upload_directory(script_dir, 'kaleidoscope')
        print(f"Deployed to s3://{self.bucket}/kaleidoscope/")
        return f"s3://{self.bucket}/kaleidoscope/"

def deploy_to_aws():
    deployer = AWSDeployer()
    return deployer.deploy()

if __name__ == "__main__":
    deploy_to_aws()
