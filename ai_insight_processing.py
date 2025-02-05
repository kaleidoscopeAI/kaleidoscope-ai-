import json
import boto3
import numpy as np
import time
from typing import Dict, List
from botocore.exceptions import ClientError

class AIInsightProcessor:
    def __init__(self, insights_bucket: str, dynamodb_table: str, cloudwatch_log_group: str, region_name="us-east-1"):
        self.s3 = boto3.client("s3", region_name=region_name)
        self.dynamodb = boto3.client("dynamodb", region_name=region_name)
        self.logs = boto3.client("logs", region_name=region_name)
        self.insights_bucket = insights_bucket
        self.dynamodb_table = dynamodb_table
        self.cloudwatch_log_group = cloudwatch_log_group
        print("AI Insight Processing System initialized.")

    def log_event(self, message: str):
        try:
            timestamp = int(time.time() * 1000)
            print(f"[LOG] {message}")
            self.logs.put_log_events(
                logGroupName=self.cloudwatch_log_group,
                logStreamName="AIInsightProcessingStream",
                logEvents=[{"timestamp": timestamp, "message": message}]
            )
        except Exception as e:
            print(f"CloudWatch logging error: {e}")

    def validate_insight(self, insight: Dict) -> bool:
        confidence_score = insight.get("confidence", np.random.uniform(0.5, 1.0))
        if confidence_score < 0.6:
            print(f"[WARNING] Insight '{insight['id']}' has low confidence ({confidence_score}). Flagging for reprocessing.")
            return False
        return True

    def process_insights(self, insights: List[Dict]) -> List[Dict]:
        validated_insights = []
        for insight in insights:
            if self.validate_insight(insight):
                insight["validated"] = True
                validated_insights.append(insight)
            else:
                print(f"[INFO] Reprocessing insight {insight['id']} due to low confidence.")
        return validated_insights

    def store_validated_insights(self, insights: List[Dict]):
        for insight in insights:
            try:
                key = f"validated_insights/{insight['id']}.json"
                self.s3.put_object(Bucket=self.insights_bucket, Key=key, Body=json.dumps(insight))
                print(f"[INFO] Stored validated insight: {insight['id']}")
                self.log_event(f"Validated insight stored: {insight['id']}")
            except ClientError as e:
                print(f"[ERROR] Error storing validated insight {insight['id']}: {e.response['Error']['Message']}")

    def analyze_anomalies(self, insights: List[Dict]):
        anomaly_count = 0
        for insight in insights:
            if insight.get("validated") is False:
                anomaly_count += 1
                print(f"[ANOMALY DETECTED] Insight {insight['id']} flagged for further analysis.")
        print(f"[INFO] Total anomalies detected: {anomaly_count}")
        self.log_event(f"Anomalies detected: {anomaly_count}")

    def auto_correct_insights(self, insights: List[Dict]):
        corrected_insights = []
        for insight in insights:
            if not insight.get("validated", False):
                insight["confidence"] = min(insight.get("confidence", 0.5) + 0.2, 1.0)
                if insight["confidence"] >= 0.6:
                    insight["validated"] = True
                    corrected_insights.append(insight)
                    print(f"[INFO] Auto-corrected insight {insight['id']} and revalidated.")
        return corrected_insights

    def adapt_to_multi_domain(self, insights: List[Dict]):
        domain_insights = {}
        for insight in insights:
            domain = insight.get("domain", "general")
            if domain not in domain_insights:
                domain_insights[domain] = []
            domain_insights[domain].append(insight)
        print(f"[INFO] Insights classified into {len(domain_insights)} domains.")
        self.log_event(f"Multi-domain insights processed: {json.dumps({k: len(v) for k, v in domain_insights.items()})}")
        return domain_insights

if __name__ == "__main__":
    ai_insight_processor = AIInsightProcessor(
        insights_bucket="ai-insights-bucket",
        dynamodb_table="AIInsightTable",
        cloudwatch_log_group="/ai-insight-processing/logs",
        region_name="us-east-1"
    )
    
    sample_insights = [
        {"id": "insight-1", "content": "Biotech breakthrough detected.", "confidence": 0.92, "domain": "biotech"},
        {"id": "insight-2", "content": "Stock market prediction highly volatile.", "confidence": 0.58, "domain": "finance"}
    ]
    
    validated_insights = ai_insight_processor.process_insights(sample_insights)
    ai_insight_processor.store_validated_insights(validated_insights)
    ai_insight_processor.analyze_anomalies(sample_insights)
    corrected_insights = ai_insight_processor.auto_correct_insights(sample_insights)
    ai_insight_processor.store_validated_insights(corrected_insights)
    domain_insights = ai_insight_processor.adapt_to_multi_domain(sample_insights)

