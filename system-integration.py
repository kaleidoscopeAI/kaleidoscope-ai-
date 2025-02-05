# system_integration.py

import asyncio
import boto3
import pandas as pd
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enhanced_scientific_bot import EnhancedScientificBot
from quantum_system_enhanced import QuantumSystemManager
import websockets
import json
import logging
from rich.console import Console
from concurrent.futures import ThreadPoolExecutor

@dataclass
class SystemQuery:
    """Structure for system queries."""
    query_text: str
    data_ref: Optional[str] = None  # S3 reference if applicable
    query_type: str = "general"
    priority: int = 1

class IntegratedSystemManager:
    """Manages integration between quantum system and scientific chatbot."""
    
    def __init__(self, config_path: str = "config/system_config.yaml"):
        self.console = Console()
        self.quantum_system = QuantumSystemManager()
        self.scientific_bot = EnhancedScientificBot()
        self.s3 = boto3.client('s3')
        self.setup_logging()
        
        # Initialize communication channels
        self.message_queue = asyncio.Queue()
        self.response_queue = asyncio.Queue()
        
    def setup_logging(self):
        """Configure system-wide logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('system_integration.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def start_system(self):
        """Initialize and start all system components."""
        try:
            # Start quantum system
            await self.quantum_system.initialize_system("config/quantum_config.yaml")
            
            # Start WebSocket server for real-time communication
            await self.start_websocket_server()
            
            # Start message processing
            await self.process_messages()
            
            self.logger.info("System integration started successfully")
            
        except Exception as e:
            self.logger.error(f"System startup failed: {str(e)}")
            raise

    async def start_websocket_server(self):
        """Start WebSocket server for real-time communication."""
        async def handler(websocket, path):
            try:
                async for message in websocket:
                    # Parse incoming message
                    data = json.loads(message)
                    query = SystemQuery(**data)
                    
                    # Process query
                    response = await self.handle_query(query)
                    
                    # Send response
                    await websocket.send(json.dumps(response))
                    
            except Exception as e:
                self.logger.error(f"WebSocket error: {str(e)}")

        self.server = await websockets.serve(handler, "localhost", 8765)

    async def handle_query(self, query: SystemQuery) -> Dict[str, Any]:
        """Handle incoming queries and route to appropriate component."""
        try:
            # Load data if reference provided
            data = None
            if query.data_ref:
                data = await self.load_data(query.data_ref)
            
            # Process based on query type
            if query.query_type == "quantum":
                response = await self.quantum_system.process_query(query.query_text)
                
            elif query.query_type == "analysis":
                response = await self.scientific_bot.analyze_data(query.query_text, data)
                
            else:
                # Determine best processor based on query content
                processor = self._determine_processor(query.query_text)
                response = await processor.process_query(query.query_text, data)
            
            return {
                "status": "success",
                "response": response,
                "query_id": id(query)
            }
            
        except Exception as e:
            self.logger.error(f"Query handling error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "query_id": id(query)
            }

    async def load_data(self, data_ref: str) -> pd.DataFrame:
        """Load data from S3 reference."""
        try:
            # Extract bucket and key from reference
            bucket, key = data_ref.split('/', 1)
            
            # Download file
            response = await asyncio.to_thread(
                self.s3.get_object,
                Bucket=bucket,
                Key=key
            )
            
            # Parse based on file type
            if key.endswith('.csv'):
                return pd.read_csv(response['Body'])
            elif key.endswith('.json'):
                return pd.read_json(response['Body'])
            else:
                raise ValueError(f"Unsupported file type: {key}")
                
        except Exception as e:
            self.logger.error(f"Data loading error: {str(e)}")
            raise

    def _determine_processor(self, query: str) -> Any:
        """Determine best processor based on query content."""
        # Simple keyword-based routing
        quantum_keywords = {'quantum', 'node', 'process', 'optimize'}
        analysis_keywords = {'analyze', 'data', 'statistical', 'trend'}
        
        query_words = set(query.lower().split())
        
        if len(query_words & quantum_keywords) > len(query_words & analysis_keywords):
            return self.quantum_system
        else:
            return self.scientific_bot

    async def process_messages(self):
        """Process messages from the queue."""
        while True:
            try:
                message = await self.message_queue.get()
                
                # Process message
                response = await self.handle_query(SystemQuery(**message))
                
                # Put response in queue
                await self.response_queue.put(response)
                
            except Exception as e:
                self.logger.error(f"Message processing error: {str(e)}")

# Example usage:
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Initialize integrated system
        system = IntegratedSystemManager()
        
        # Start system
        await system.start_system()
        
        # Example queries
        queries = [
            {
                "query_text": "Analyze the correlation in quantum node performance",
                "query_type": "analysis",
                "data_ref": "quantum-bucket/node_metrics.csv"
            },
            {
                "query_text": "Optimize quantum processing parameters",
                "query_type": "quantum"
            }
        ]
        
        # Process queries
        for query in queries:
            response = await system.handle_query(SystemQuery(**query))
            print(f"Query Response: {response}")
        
    asyncio.run(main())
