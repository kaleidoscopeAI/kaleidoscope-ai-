
import numpy as np
import logging

logging.basicConfig(
    filename="kaleidoscope_engine.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class KaleidoscopeEngine:
    def __init__(self):
        self.insights = []

    def process_data(self, data):
        try:
            numerical_insights = self._analyze_numerical_data(data.get("numerical", []))
            text_insights = self._analyze_text_data(data.get("text", []))
            combined_insights = numerical_insights + text_insights
            self.insights.extend(combined_insights)
            logging.info(f"Processed data into {len(combined_insights)} insights.")
            return {"insights": combined_insights}
        except Exception as e:
            logging.error(f"Error processing data: {e}")
            raise

    def _analyze_numerical_data(self, numbers):
        if not numbers:
            return []
        mean = np.mean(numbers)
        std_dev = np.std(numbers)
        trend = np.polyfit(range(len(numbers)), numbers, 1)[0]
        return [{"type": "numerical_analysis", "mean": mean, "std_dev": std_dev, "trend": trend}]

    def _analyze_text_data(self, texts):
        if not texts:
            return []
        return [{"type": "text_analysis", "text": text, "length": len(text)} for text in texts]
