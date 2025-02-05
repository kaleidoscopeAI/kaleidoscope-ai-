import json
import boto3
import numpy as np
import time
from typing import Dict, List
from botocore.exceptions import ClientError

class SuperNodeSystem:
    def __init__(self, insights_bucket: str, dynamodb_table: str, cloudwatch_log_group: str, region_name="us-east-1"):
        self.s3 = boto3.client("s3", region_name=region_name)
        self.dynamodb = boto3.client("dynamodb", region_name=region_name)
        self.logs = boto3.client("logs", region_name=region_name)
        self.insights_bucket = insights_bucket
        self.dynamodb_table = dynamodb_table
        self.cloudwatch_log_group = cloudwatch_log_group
        print("Super Node System initialized.")

    def log_event(self, message: str):
        try:
            timestamp = int(time.time() * 1000)
            print(f"[LOG] {message}")
            self.logs.put_log_events(
                logGroupName=self.cloudwatch_log_group,
                logStreamName="SuperNodeStream",
                logEvents=[{"timestamp": timestamp, "message": message}]
            )
        except Exception as e:
            print(f"CloudWatch logging error: {e}")

    def fetch_super_node_insights(self, super_node_id: str) -> List[Dict]:
        try:
            response = self.s3.list_objects_v2(Bucket=self.insights_bucket, Prefix=f"{super_node_id}/", MaxKeys=50)
            insights = []
            if "Contents" in response:
                for obj in response["Contents"]:
                    key = obj["Key"]
                    data = self.s3.get_object(Bucket=self.insights_bucket, Key=key)["Body"].read().decode("utf-8")
                    insights.append(json.loads(data))
            if not insights:
                print(f"[INFO] No insights found for Super Node {super_node_id}.")
            return insights
        except ClientError as e:
            print(f"[ERROR] Error fetching insights for {super_node_id}: {e.response['Error']['Message']}")
            return []

if __name__ == "__main__":
    supernode_system = SuperNodeSystem(
        insights_bucket="supernode-insights-bucket",
        dynamodb_table="SuperNodeTable",
        cloudwatch_log_group="/supernode-system/logs",
        region_name="us-east-1"
    )
    
    clusters = supernode_system.cluster_super_nodes()
    print("[RESULT] Super Node Clusters:", clusters)

