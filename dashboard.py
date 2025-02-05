from flask import Flask, render_template, jsonify
import boto3
import json

app = Flask(__name__)

# AWS Configuration
REGION = "us-east-1"
NODE_STATUS_TABLE = "NodeStatusTable"
INSIGHT_BUCKET = "insights-bucket"

# Initialize AWS Clients
dynamodb = boto3.resource("dynamodb", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)

@app.route("/")
def home():
    """Render the real-time system monitoring dashboard."""
    return render_template("dashboard.html")

@app.route("/node_status", methods=["GET"])
def node_status():
    """Fetch node statuses from AWS DynamoDB."""
    table = dynamodb.Table(NODE_STATUS_TABLE)
    try:
        response = table.scan()
        return jsonify(response.get("Items", [])), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch node statuses: {str(e)}"}), 500

@app.route("/anomalies", methods=["GET"])
def anomalies():
    """Fetch anomaly data from AWS S3."""
    try:
        response = s3.list_objects_v2(Bucket=INSIGHT_BUCKET, Prefix="anomalies/")
        anomalies = []
        if "Contents" in response:
            for obj in response["Contents"]:
                key = obj["Key"]
                anomaly_data = s3.get_object(Bucket=INSIGHT_BUCKET, Key=key)["Body"].read().decode("utf-8")
                anomalies.append(json.loads(anomaly_data))
        return jsonify(anomalies), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch anomalies: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)

