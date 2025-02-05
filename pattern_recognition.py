# pattern_recognition.py

import numpy as np
from typing import List, Dict

class PatternRecognition:
    @staticmethod
    def extract_features(raw_data: List[Dict]) -> List[Dict]:
        """
        Extract features from raw data, ensuring compatibility with node initialization traits.
        """
        return [
            {
                "feature_1": np.random.rand(),  # Randomized for this example
                "feature_2": np.random.rand(),  # Simulated feature
                "feature_3": np.log(1 + data["raw_value"]),  # Example: Log-scaled feature
            }
            for data in raw_data
        ]

    @staticmethod
    def normalize_features(features: List[Dict]) -> List[Dict]:
        """
        Normalize extracted features for consistent scaling across nodes.
        """
        normalized = []
        for feature_set in features:
            total = sum(feature_set.values())
            normalized.append({k: v / total if total > 0 else 0 for k, v in feature_set.items()})
        return normalized
