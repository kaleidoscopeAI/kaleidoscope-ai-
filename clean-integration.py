# system_integration.py

import asyncio
import boto3
import pandas as pd
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enhanced_scientific_bot import EnhancedScientificBot
from quantum_system_enhanced import QuantumSystemManager

@dataclass
class SystemResponse:
    """Standardized system response format."""
    message: str
    data: Optional[Dict[str, Any]] = None
    visualizations: Optional[List[Any]] = None
    error: Optional[str] = None

class IntegratedSystem:
    """Integration layer between quantum system and scientific chatbot."""
    
    def __init__(self):
        self.quantum_system = QuantumSystemManager()
        self.scientific_bot = EnhancedScientificBot()
        self.s3_client = boto3.client('s3')
        
    async def initialize(self):
        """Initialize both systems."""
        await self.quantum_system.initialize_system()
        print("System initialized successfully")

    async def process_query(self, query: str, data: Optional[pd.DataFrame] = None) -> SystemResponse:
        """Process incoming queries and route to appropriate system."""
        try:
            # Determine query type
            if self._is_quantum_query(query):
                response = await self._handle_quantum_query(query)
            else:
                response = await self._handle_scientific_query(query, data)
                
            return response
            
        except Exception as e:
            return SystemResponse(
                message="Error processing query",
                error=str(e)
            )

    def _is_quantum_query(self, query: str) -> bool:
        """Determine if query is related to quantum system."""
        quantum_keywords = {'quantum', 'node', 'process', 'system', 'optimize'}
        query_words = set(query.lower().split())
        return bool(query_words & quantum_keywords)

    async def _handle_quantum_query(self, query: str) -> SystemResponse:
        """Handle quantum system related queries."""
        try:
            result = await self.quantum_system.process_query(query)
            return SystemResponse(
                message="Quantum query processed",
                data=result
            )
        except Exception as e:
            return SystemResponse(
                message="Quantum processing error",
                error=str(e)
            )

    async def _handle_scientific_query(self, query: str, data: Optional[pd.DataFrame]) -> SystemResponse:
        """Handle scientific/data analysis queries."""
        try:
            result = await self.scientific_bot.analyze_data(query, data)
            return SystemResponse(
                message="Analysis complete",
                data=result.statistics,
                visualizations=result.visualizations
            )
        except Exception as e:
            return SystemResponse(
                message="Analysis error",
                error=str(e)
            )

    async def process_data_file(self, file_path: str) -> pd.DataFrame:
        """Process uploaded data files."""
        try:
            if file_path.endswith('.csv'):
                return pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                return pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_path}")
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            raise

def main():
    """Main function to demonstrate system usage."""
    async def run_example():
        # Initialize system
        system = IntegratedSystem()
        await system.initialize()
        
        # Example queries
        queries = [
            "Analyze the correlation between node performance metrics",
            "Optimize quantum processing parameters",
            "Calculate statistical distribution of processing times"
        ]
        
        # Process each query
        for query in queries:
            response = await system.process_query(query)
            print(f"\nQuery: {query}")
            print(f"Response: {response.message}")
            if response.data:
                print(f"Data: {response.data}")
            if response.error:
                print(f"Error: {response.error}")

    # Run the example
    asyncio.run(run_example())

if __name__ == "__main__":
    main()
