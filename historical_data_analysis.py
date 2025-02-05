# File: historical_data_analysis.py

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict
import logging

# Configure logging
logging.basicConfig(
    filename="historical_data_analysis.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class HistoricalDataAnalyzer:
    """
    Analyzes historical performance data for nodes and the system as a whole.
    """
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.data = None

    def load_data(self):
        """
        Loads historical data from the log file.
        """
        try:
            self.data = pd.read_csv(self.log_file)
            logging.info("Historical data loaded successfully.")
        except FileNotFoundError:
            logging.error(f"Log file {self.log_file} not found.")
            self.data = pd.DataFrame()

    def preprocess_data(self):
        """
        Prepares the data for analysis by handling missing values and formatting.
        """
        if self.data.empty:
            logging.warning("No data to preprocess.")
            return

        self.data.dropna(inplace=True)
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        logging.info("Data preprocessing completed.")

    def calculate_trends(self):
        """
        Analyzes trends in energy, knowledge, and task completion rates.

        Returns:
            Dict[str, pd.Series]: Trends for key metrics.
        """
        if self.data.empty:
            logging.warning("No data to analyze.")
            return {}

        trends = {
            'energy': self.data.groupby('timestamp')['energy'].mean(),
            'knowledge': self.data.groupby('timestamp')['knowledge'].mean(),
            'task_completion_rate': self.data.groupby('timestamp')['task_completion_rate'].mean()
        }
        logging.info("Trend analysis completed.")
        return trends

    def detect_anomalies(self, metric: str, z_threshold: float = 2.0):
        """
        Identifies anomalies in a given metric using Z-scores.

        Parameters:
            metric (str): The metric to analyze (e.g., 'energy').
            z_threshold (float): The Z-score threshold for anomalies.

        Returns:
            pd.DataFrame: Rows containing anomalies.
        """
        if metric not in self.data.columns:
            logging.warning(f"Metric {metric} not found in data.")
            return pd.DataFrame()

        mean = self.data[metric].mean()
        std = self.data[metric].std()
        self.data['z_score'] = (self.data[metric] - mean) / std
        anomalies = self.data[np.abs(self.data['z_score']) > z_threshold]
        logging.info(f"Anomalies detected in metric {metric}. Count: {len(anomalies)}")
        return anomalies

    def visualize_trends(self, trends: Dict[str, pd.Series]):
        """
        Visualizes trends for energy, knowledge, and task completion rates.
        """
        plt.figure(figsize=(15, 10))

        for i, (metric, series) in enumerate(trends.items(), 1):
            plt.subplot(2, 2, i)
            series.plot(label=metric)
            plt.title(f"{metric.capitalize()} Trends")
            plt.xlabel("Timestamp")
            plt.ylabel(metric.capitalize())
            plt.legend()

        plt.tight_layout()
        plt.show()

# Example Usage
if __name__ == "__main__":
    # Example log file
    log_file = "performance_data.csv"

    # Initialize the analyzer
    analyzer = HistoricalDataAnalyzer(log_file)

    # Load and preprocess data
    analyzer.load_data()
    analyzer.preprocess_data()

    # Calculate trends
    trends = analyzer.calculate_trends()

    # Visualize trends
    if trends:
        analyzer.visualize_trends(trends)

    # Detect anomalies in energy levels
    anomalies = analyzer.detect_anomalies(metric='energy')
    print("Anomalies:", anomalies)
