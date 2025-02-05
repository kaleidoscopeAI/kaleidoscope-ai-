import json
import boto3
import time
from typing import Dict, List
from botocore.exceptions import ClientError

class AWSScalabilityOptimizer:
    def __init__(self, insights_bucket: str, dynamodb_table: str, cloudwatch_log_group: str, auto_scaling_group: str, region_name="us-east-1"):
        self.s3 = boto3.client("s3", region_name=region_name)
        self.dynamodb = boto3.client("dynamodb", region_name=region_name)
        self.logs = boto3.client("logs", region_name=region_name)
        self.autoscaling = boto3.client("autoscaling", region_name=region_name)
        self.insights_bucket = insights_bucket
        self.dynamodb_table = dynamodb_table
        self.cloudwatch_log_group = cloudwatch_log_group
        self.auto_scaling_group = auto_scaling_group
        print("AWS Scalability Optimization System initialized.")

    def log_event(self, message: str):
        try:
            timestamp = int(time.time() * 1000)
            print(f"[LOG] {message}")
            self.logs.put_log_events(
                logGroupName=self.cloudwatch_log_group,
                logStreamName="AWSScalabilityStream",
                logEvents=[{"timestamp": timestamp, "message": message}]
            )
        except Exception as e:
            print(f"CloudWatch logging error: {e}")

    def monitor_system_load(self) -> Dict:
        try:
            metrics = self.logs.describe_log_streams(logGroupName=self.cloudwatch_log_group)
            print(f"[INFO] System load metrics retrieved successfully.")
            return metrics
        except ClientError as e:
            print(f"[ERROR] Error retrieving system metrics: {e.response['Error']['Message']}")
            return {}

    def optimize_scaling(self, load_threshold: float = 0.75):
        metrics = self.monitor_system_load()
        current_load = metrics.get("logStreams", [{}])[0].get("uploadSequenceToken", 0)
        
        if current_load > load_threshold:
            try:
                print("[INFO] Scaling up infrastructure due to high load.")
                self.autoscaling.set_desired_capacity(
                    AutoScalingGroupName=self.auto_scaling_group,
                    DesiredCapacity=int(current_load * 1.2),
                    HonorCooldown=True
                )
                self.log_event("AWS Auto Scaling increased capacity due to system load.")
            except ClientError as e:
                print(f"[ERROR] Error adjusting auto-scaling: {e.response['Error']['Message']}")
        else:
            print("[INFO] System load is stable, no scaling adjustments needed.")

    def cleanup_resources(self):
        try:
            print("[INFO] Checking for outdated insights in S3 and DynamoDB.")
            response = self.s3.list_objects_v2(Bucket=self.insights_bucket, Prefix="archived/")
            if "Contents" in response:
                for obj in response["Contents"]:
                    print(f"[INFO] Deleting outdated insight: {obj['Key']}")
                    self.s3.delete_object(Bucket=self.insights_bucket, Key=obj["Key"])
            
            self.log_event("Outdated insights cleaned up from storage.")
        except ClientError as e:
            print(f"[ERROR] Error cleaning up resources: {e.response['Error']['Message']}")

if __name__ == "__main__":
    aws_scalability = AWSScalabilityOptimizer(
        insights_bucket="ai-insights-bucket",
        dynamodb_table="AIInsightTable",
        cloudwatch_log_group="/aws-scalability/logs",
        auto_scaling_group="AIProcessingAutoScalingGroup",
        region_name="us-east-1"
    )
    
    aws_scalability.monitor_system_load()
    aws_scalability.optimize_scaling()
    aws_scalability.cleanup_resources()

