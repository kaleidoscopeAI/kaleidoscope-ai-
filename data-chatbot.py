# scientific_chatbot.py

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import pandas as pd
import numpy as np
from typing import Dict, List, Union, Any
import plotly.express as px
from scipy import stats
import yfinance as yf

class ScientificDataBot:
    """
    Scientific and Financial Data Analysis Chatbot using PaLM or Llama2
    with specialized data processing capabilities.
    """
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        """
        Initialize with smaller but efficient open source model.
        Can be replaced with larger models like Llama2 if more compute is available.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.data_cache = {}
        
    async def process_query(self, query: str, data: Union[pd.DataFrame, None] = None) -> Dict[str, Any]:
        """Process user query and return analyzed response."""
        try:
            # Identify query type
            query_type = self._classify_query(query)
            
            if query_type == "data_analysis":
                return await self._handle_data_analysis(query, data)
            elif query_type == "financial":
                return await self._handle_financial_query(query)
            else:
                return await self._generate_response(query)
                
        except Exception as e:
            return {
                "response": f"Error processing query: {str(e)}",
                "error": True
            }

    def _classify_query(self, query: str) -> str:
        """Classify the type of query for specialized handling."""
        query = query.lower()
        
        # Data analysis keywords
        if any(word in query for word in ["analyze", "correlation", "statistical", "dataset"]):
            return "data_analysis"
            
        # Financial keywords
        if any(word in query for word in ["stock", "price", "market", "financial"]):
            return "financial"
            
        return "general"

    async def _handle_data_analysis(self, query: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Handle data analysis queries with statistical processing."""
        try:
            # Basic statistical analysis
            stats_summary = {
                "mean": data.mean().to_dict(),
                "median": data.median().to_dict(),
                "std": data.std().to_dict()
            }
            
            # Correlation analysis if multiple numeric columns
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                correlation = data[numeric_cols].corr()
                stats_summary["correlation"] = correlation.to_dict()
            
            # Generate visualization if appropriate
            if len(numeric_cols) > 0:
                fig = px.scatter(data, x=numeric_cols[0], y=numeric_cols[1] if len(numeric_cols) > 1 else None)
                stats_summary["visualization"] = fig
            
            # Generate natural language response
            response = self._generate_analysis_response(stats_summary, query)
            
            return {
                "response": response,
                "statistics": stats_summary,
                "error": False
            }
            
        except Exception as e:
            return {"response": f"Analysis error: {str(e)}", "error": True}

    async def _handle_financial_query(self, query: str) -> Dict[str, Any]:
        """Handle financial data queries using yfinance."""
        try:
            # Extract ticker symbols from query
            symbols = self._extract_symbols(query)
            if not symbols:
                return {"response": "No stock symbols found in query", "error": True}
            
            # Fetch financial data
            data = {}
            for symbol in symbols:
                stock = yf.Ticker(symbol)
                data[symbol] = {
                    "info": stock.info,
                    "history": stock.history(period="1mo").to_dict(),
                    "financials": stock.financials.to_dict() if hasattr(stock, 'financials') else None
                }
            
            # Generate analysis
            analysis = self._analyze_financial_data(data)
            
            return {
                "response": analysis["summary"],
                "data": data,
                "analysis": analysis,
                "error": False
            }
            
        except Exception as e:
            return {"response": f"Financial analysis error: {str(e)}", "error": True}

    async def _generate_response(self, query: str) -> Dict[str, Any]:
        """Generate response using the language model."""
        try:
            # Prepare input
            inputs = self.tokenizer(query, return_tensors="pt", padding=True)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_length=150,
                    num_return_sequences=1,
                    temperature=0.7
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return {
                "response": response,
                "error": False
            }
            
        except Exception as e:
            return {"response": f"Generation error: {str(e)}", "error": True}

    def _generate_analysis_response(self, stats: Dict[str, Any], query: str) -> str:
        """Generate natural language response from statistical analysis."""
        response_parts = []
        
        # Add mean analysis
        if "mean" in stats:
            response_parts.append("Statistical Summary:")
            for key, value in stats["mean"].items():
                response_parts.append(f"- Average {key}: {value:.2f}")
        
        # Add correlation insights
        if "correlation" in stats:
            response_parts.append("\nCorrelation Analysis:")
            corr = stats["correlation"]
            # Find strongest correlations
            for col1 in corr:
                for col2 in corr[col1]:
                    if col1 != col2 and abs(corr[col1][col2]) > 0.5:
                        response_parts.append(
                            f"- Strong {'positive' if corr[col1][col2] > 0 else 'negative'} "
                            f"correlation between {col1} and {col2}: {corr[col1][col2]:.2f}"
                        )
        
        return "\n".join(response_parts)

    def _analyze_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform financial data analysis."""
        analysis = {"summary": [], "metrics": {}}
        
        for symbol, stock_data in data.items():
            # Basic metrics
            if "history" in stock_data:
                history = pd.DataFrame(stock_data["history"])
                analysis["metrics"][symbol] = {
                    "volatility": history["Close"].std(),
                    "returns": (history["Close"].iloc[-1] / history["Close"].iloc[0] - 1) * 100,
                    "volume_trend": history["Volume"].mean()
                }
            
            # Generate summary
            analysis["summary"].append(
                f"Analysis for {symbol}:\n"
                f"- Volatility: {analysis['metrics'][symbol]['volatility']:.2f}\n"
                f"- Monthly Return: {analysis['metrics'][symbol]['returns']:.2f}%\n"
                f"- Average Volume: {analysis['metrics'][symbol]['volume_trend']:,.0f}"
            )
        
        analysis["summary"] = "\n\n".join(analysis["summary"])
        return analysis

    def _extract_symbols(self, query: str) -> List[str]:
        """Extract stock symbols from query."""
        # Simple symbol extraction - can be enhanced with NLP
        words = query.upper().split()
        # Basic filtering for likely symbols (2-5 uppercase letters)
        symbols = [word for word in words if word.isalpha() and 2 <= len(word) <= 5]
        return symbols

# Example usage:
if __name__ == "__main__":
    import asyncio
    
    async def main():
        bot = ScientificDataBot()
        
        # Example data analysis query
        data = pd.DataFrame({
            'x': np.random.normal(0, 1, 100),
            'y': np.random.normal(0, 1, 100)
        })
        result = await bot.process_query("Analyze the correlation in this dataset", data)
        print(result['response'])
        
        # Example financial query
        result = await bot.process_query("Analyze the stock price for AAPL")
        print(result['response'])

    asyncio.run(main())
