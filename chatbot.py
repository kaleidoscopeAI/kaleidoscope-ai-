from flask import Flask, request, jsonify
import openai
import boto3
import json
import os

app = Flask(__name__)

# AWS Configuration
REGION = "us-east-1"
NODE_STATUS_TABLE = "NodeStatusTable"
SECRETS_MANAGER_ARN = "arn:aws:secretsmanager:us-east-1:123456789012:secret:OpenAIKey"

# Initialize AWS Clients
dynamodb = boto3.resource("dynamodb", region_name=REGION)
secrets_manager = boto3.client("secretsmanager", region_name=REGION)

# Securely Retrieve OpenAI API Key
def get_openai_api_key():
    try:
        secret = secrets_manager.get_secret_value(SecretId=SECRETS_MANAGER_ARN)
        secret_data = json.loads(secret["SecretString"])
        return secret_data["openai_api_key"]
    except Exception as e:
        print(f"[ERROR] Unable to retrieve OpenAI API Key: {e}")
        return None

openai.api_key = get_openai_api_key()

@app.route("/chat", methods=["POST"])
def chat():
    """Handles chatbot interactions by fetching system insights and node status."""
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    system_status = get_system_status()
    response = generate_ai_response(user_input, system_status)
    return jsonify({"response": response}), 200

def get_system_status():
    """Fetches system-wide node statuses from DynamoDB."""
    table = dynamodb.Table(NODE_STATUS_TABLE)
    try:
        response = table.scan()
        return response.get("Items", [])
    except Exception as e:
        return {"error": f"Failed to fetch system status: {str(e)}"}

def generate_ai_response(user_input: str, system_status: list) -> str:
    """Generates an AI response based on user input and system insights."""
    prompt = f"System Status: {json.dumps(system_status, indent=2)}\nUser: {user_input}\nAI:"
    try:
        ai_response = openai.Completion.create(
            engine="gpt-4",
            prompt=prompt,
            max_tokens=150
        )
        return ai_response["choices"][0]["text"].strip()
    except Exception as e:
        return f"[ERROR] AI Response Generation Failed: {e}"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

