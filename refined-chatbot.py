# enhanced_scientific_bot.py

import torch
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Any
from transformers import AutoModelForCausalLM, AutoTokenizer
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import yfinance as yf
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
import logging
from concurrent.futures import ThreadPoolExecutor

@dataclass
class AnalysisResult:
    """Structured container for analysis results."""
    summary: str
    statistics: Dict[str, Any]
    visualizations: List[Any]
    error: Optional[str] = None

class DataProcessor:
    """Handles data preprocessing and validation."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
    
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data with advanced cleaning and normalization."""
        # Handle missing values
        numeric_data = data.select_dtypes(include=[np.number])
        categorical_data = data.select_dtypes(exclude=[np.number])
        
        # Fill numeric missing values with median
        numeric_data = numeric_data.fillna(numeric_data.median())
        
        # Fill categorical missing values with mode
        categorical_data = categorical_data.fillna(categorical_data.mode().iloc[0])
        
        # Scale numeric features
        scaled_data = pd.DataFrame(
            self.scaler.fit_transform(numeric_data),
            columns=numeric_data.columns,
            index=numeric_data.index
        )
        
        # Combine processed data
        processed_data = pd.concat([scaled_data, categorical_data], axis=1)
        return processed_data

    def detect_outliers(self, data: pd.DataFrame) -> Dict[str, List[int]]:
        """Detect outliers using multiple methods."""
        outliers = {}
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            # Z-score method
            z_scores = np.abs(stats.zscore(data[col]))
            z_outliers = np.where(z_scores > 3)[0]
            
            # IQR method
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            iqr_outliers = data[col][
                (data[col] < (Q1 - 1.5 * IQR)) | 
                (data[col] > (Q3 + 1.5 * IQR))
            ].index
            
            # Combine results
            outliers[col] = list(set(z_outliers) | set(iqr_outliers))
        
        return outliers

class VisualizationEngine:
    """Handles advanced data visualization."""
    
    def create_analysis_dashboard(self, data: pd.DataFrame, analysis: Dict[str, Any]) -> List[go.Figure]:
        """Create comprehensive analysis dashboard."""
        figures = []
        
        # Distribution plots
        for col in data.select_dtypes(include=[np.number]).columns:
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=data[col], name=col))
            fig.update_layout(title=f"Distribution of {col}")
            figures.append(fig)
        
        # Correlation heatmap
        if len(data.select_dtypes(include=[np.number]).columns) > 1:
            corr_matrix = data.corr()
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns
            ))
            fig.update_layout(title="Correlation Heatmap")
            figures.append(fig)
        
        # Time series if applicable
        if 'date' in data.columns or data.index.dtype == 'datetime64[ns]':
            for col in data.select_dtypes(include=[np.number]).columns:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data.index, y=data[col], mode='lines', name=col))
                fig.update_layout(title=f"Time Series of {col}")
                figures.append(fig)
        
        return figures

class EnhancedScientificBot:
    """Refined scientific and financial analysis chatbot."""
    
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.data_processor = DataProcessor()
        self.visualization_engine = VisualizationEngine()
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging system."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    async def analyze_data(self, query: str, data: Optional[pd.DataFrame] = None) -> AnalysisResult:
        """Perform comprehensive data analysis based on query."""
        try:
            # Process query intent
            intent = self._analyze_intent(query)
            
            if data is not None:
                # Preprocess data
                processed_data = self.data_processor.preprocess_data(data)
                
                # Detect outliers
                outliers = self.data_processor.detect_outliers(processed_data)
                
                # Statistical analysis
                stats_summary = self._generate_statistics(processed_data)
                
                # Create visualizations
                visualizations = self.visualization_engine.create_analysis_dashboard(
                    processed_data, stats_summary
                )
                
                # Generate natural language summary
                summary = await self._generate_summary(stats_summary, outliers, intent)
                
                return AnalysisResult(
                    summary=summary,
                    statistics=stats_summary,
                    visualizations=visualizations
                )
            
            else:
                # Handle non-data queries
                response = await self._generate_response(query)
                return AnalysisResult(
                    summary=response,
                    statistics={},
                    visualizations=[]
                )
                
        except Exception as e:
            self.logger.error(f"Analysis error: {str(e)}")
            return AnalysisResult(
                summary="Error during analysis",
                statistics={},
                visualizations=[],
                error=str(e)
            )

    def _analyze_intent(self, query: str) -> Dict[str, float]:
        """Analyze query intent using keyword matching and scoring."""
        intent_keywords = {
            'statistical': ['mean', 'average', 'median', 'correlation', 'distribution'],
            'financial': ['stock', 'price', 'market', 'trend', 'financial'],
            'predictive': ['forecast', 'predict', 'future', 'trend', 'projection'],
            'exploratory': ['explore', 'analyze', 'examine', 'investigate', 'study']
        }
        
        scores = {intent: 0.0 for intent in intent_keywords}
        query_words = query.lower().split()
        
        for intent, keywords in intent_keywords.items():
            for word in query_words:
                if word in keywords:
                    scores[intent] += 1.0
                    
        # Normalize scores
        total = sum(scores.values()) + 1e-10
        return {k: v/total for k, v in scores.items()}

    def _generate_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive statistical analysis."""
        stats_summary = {}
        
        # Basic statistics
        stats_summary['basic'] = {
            'mean': data.mean().to_dict(),
            'median': data.median().to_dict(),
            'std': data.std().to_dict(),
            'skew': data.skew().to_dict()
        }
        
        # Correlation analysis
        numeric_data = data.select_dtypes(include=[np.number])
        if len(numeric_data.columns) > 1:
            stats_summary['correlation'] = numeric_data.corr().to_dict()
        
        # Time series analysis if applicable
        if 'date' in data.columns or data.index.dtype == 'datetime64[ns]':
            stats_summary['temporal'] = {
                'trend': self._calculate_trends(numeric_data),
                'seasonality': self._detect_seasonality(numeric_data)
            }
        
        return stats_summary

    async def _generate_summary(self, stats: Dict[str, Any], outliers: Dict[str, List[int]], 
                              intent: Dict[str, float]) -> str:
        """Generate natural language summary of analysis."""
        summary_parts = []
        
        # Add statistical insights based on intent
        if intent['statistical'] > 0.3:
            summary_parts.append(self._summarize_statistics(stats['basic']))
        
        if intent['financial'] > 0.3 and 'temporal' in stats:
            summary_parts.append(self._summarize_trends(stats['temporal']))
        
        if outliers:
            summary_parts.append(self._summarize_outliers(outliers))
        
        # Generate comprehensive summary using language model
        summary = " ".join(summary_parts)
        enhanced_summary = await self._enhance_summary_with_llm(summary)
        
        return enhanced_summary

    async def _enhance_summary_with_llm(self, base_summary: str) -> str:
        """Enhance summary using language model."""
        prompt = f"Enhance this technical summary in a clear, professional way: {base_summary}"
        
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=200,
                num_return_sequences=1,
                temperature=0.7
            )
        
        enhanced_summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return enhanced_summary

if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Example usage
        bot = EnhancedScientificBot()
        
        # Create sample data
        data = pd.DataFrame({
            'x': np.random.normal(0, 1, 100),
            'y': np.random.normal(0, 1, 100),
            'date': pd.date_range(start='2023-01-01', periods=100)
        })
        
        # Analyze data
        result = await bot.analyze_data(
            "Analyze the trends and correlations in this dataset", 
            data
        )
        
        print("Analysis Summary:")
        print(result.summary)
        print("\nStatistics:")
        print(result.statistics)
        
        # Display first visualization
        if result.visualizations:
            result.visualizations[0].show()

    asyncio.run(main())
