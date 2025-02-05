import json
import time
import networkx as nx
import boto3
from typing import Dict, List, Any

# AWS Configuration
MEMORY_BUCKET = "kaleidoscope-memory"
REGION = "us-east-1"

# Initialize AWS Clients
s3 = boto3.client("s3", region_name=REGION)

class AdaptiveMemory:
    """
    Stores and retrieves long-term memory for nodes.
    """
    def __init__(self):
        self.memory_graph = nx.Graph()

    def load_memory(self):
        """ Load memory from S3. """
        try:
            response = s3.get_object(Bucket=MEMORY_BUCKET, Key="memory.json")
            memory_data = json.loads(response["Body"].read().decode("utf-8"))
            self.memory_graph = nx.node_link_graph(memory_data)
        except Exception as e:
            print(f"[WARNING] No previous memory found: {e}")

    def store_memory(self):
        """ Save memory to S3. """
        memory_data = nx.node_link_data(self.memory_graph)
        s3.put_object(Bucket=MEMORY_BUCKET, Key="memory.json", Body=json.dumps(memory_data))

    def add_insight(self, node_id: str, insight: Dict[str, Any]):
        """ Add insight to memory graph. """
        self.memory_graph.add_node(node_id, insights=insight)
        self.store_memory()

    def retrieve_insights(self, node_id: str):
        """ Retrieve past insights from memory graph. """
        return self.memory_graph.nodes[node_id]["insights"] if node_id in self.memory_graph else None

if __name__ == "__main__":
    memory = AdaptiveMemory()
    memory.load_memory()
    memory.add_insight("Node-1", {"type": "prediction", "confidence": 0.92})
    print(memory.retrieve_insights("Node-1"))

