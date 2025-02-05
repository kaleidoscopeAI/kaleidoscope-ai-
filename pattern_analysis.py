perspective_engine/core/pattern_analysis.py
Python

import numpy as np

class PatternAnalyzer:
    def __init__(self, pattern_registry: AdvancedPatternRegistry):
        self.pattern_registry = pattern_registry

    def analyze_patterns(self) -> dict:
        """Analyze patterns from the registry for insights and trends."""
        analysis = {}

        # Basic pattern statistics
        analysis['total_patterns'] = len(self.pattern_registry.patterns)
        analysis['pattern_types'] = self._get_pattern_type_distribution()

        # Stability and frequency analysis
        stable_patterns = self.pattern_registry.get_stable_patterns()
        frequent_patterns = self.pattern_registry.get_frequent_patterns()
        analysis['stable_patterns'] = [self._summarize_pattern(p) for p in stable_patterns]
        analysis['frequent_patterns'] = [self._summarize_pattern(p) for p in frequent_patterns]

        # Evolution analysis
        analysis['pattern_evolution'] = self.pattern_registry.analyze_pattern_evolution()

        # Correlation analysis
        analysis['correlations'] = self._calculate_correlations(self.pattern_registry.patterns.values())

        return analysis

    def _get_pattern_type_distribution(self) -> dict:
        """Calculate the distribution of different pattern types."""
        distribution = {}
        for pattern_data in self.pattern_registry.patterns.values():
            pattern_type = pattern_data['pattern']['type']
            distribution[pattern_type] = distribution.get(pattern_type, 0) + 1
        return distribution

    def _summarize_pattern(self, pattern: dict) -> dict:
        """Summarize key information about a pattern."""
        return {
            'id': self.pattern_registry._generate_pattern_id(pattern),
            'type': pattern['type'],
            'dimensions': pattern.get('dimensions', []),
            'strength': pattern.get('strength', 0),
            'coherence': pattern.get('coherence', 0),
            'timestamp': pattern.get('timestamp', str(np.datetime64('NaT'))),
            # Add more fields as needed
        }
    
    def _calculate_correlations(self, patterns) -> dict:
        """Calculate correlations between different pattern features."""
        correlations = {}

        # Extract relevant features for correlation analysis
        features = {
            'strength': [],
            'coherence': [],
            'num_dimensions': [],
            # Add more features as needed
        }
        for pattern_data in patterns:
            pattern = pattern_data['pattern']
            features['strength'].append(pattern.get('strength', 0))
            features['coherence'].append(pattern.get('coherence', 0))
            features['num_dimensions'].append(len(pattern.get('dimensions', [])))
            # Add more features as needed

        # Calculate correlations
        for feature1 in features:
            for feature2 in features:
                if feature1 != feature2:
                    correlation = np.corrcoef(features[feature1], features[feature2])[0, 1]
                    correlations[f"{feature1}_vs_{feature2}"] = correlation

        return correlations
    
    def get_state(self) -> dict:
        """Returns the current state of the pattern analyzer."""
        return {
            'analysis': self.analyze_patterns()
        }
