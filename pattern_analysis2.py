utils/pattern_analysis.py
Python

import numpy as np
from collections import Counter

class PatternAnalysis:

    @staticmethod
    def calculate_pattern_frequency(patterns: list) -> dict:
        """Calculate the frequency of each pattern type."""
        pattern_types = [pattern['type'] for pattern in patterns]
        return dict(Counter(pattern_types))

    @staticmethod
    def calculate_average_pattern_strength(patterns: list) -> float:
        """Calculate the average strength of patterns."""
        strengths = [pattern.get('strength', 0) for pattern in patterns]
        return np.mean(strengths) if strengths else 0

    @staticmethod
    def find_most_common_dimension(patterns: list) -> int:
      """Find the most common dimension involved in patterns."""
      dimensions = []
      for pattern in patterns:
          if 'dimensions' in pattern:
              dimensions.extend(pattern['dimensions'])
          elif 'dimension' in pattern:
              dimensions.append(pattern['dimension'])
      
      if not dimensions:
          return None

      # Find the most common dimension
      dimension_counts = Counter(dimensions)
      most_common_dimension = dimension_counts.most_common(1)[0][0]
      return most_common_dimension

    @staticmethod
    def calculate_pattern_correlations(patterns: list) -> dict:
        """Calculate correlations between different pattern attributes."""
        correlations = {}
        
        # Extract attributes from patterns
        attributes = defaultdict(list)
        for pattern in patterns:
            for key, value in pattern.items():
                if isinstance(value, (int, float)):  # Consider only numerical attributes
                    attributes[key].append(value)

        # Calculate correlations
        for key1 in attributes:
            for key2 in attributes:
                if key1 != key2:
                    correlation_key = f"{key1}_vs_{key2}"
                    if correlation_key not in correlations and f"{key2}_vs_{key1}" not in correlations:
                        correlation = np.corrcoef(attributes[key1], attributes[key2])[0, 1]
                        correlations[correlation_key] = correlation

        return correlations

    @staticmethod
    def analyze_pattern_evolution(pattern_registry: AdvancedPatternRegistry) -> dict:
        """Analyze the evolution of patterns over time."""
        evolution_data = pattern_registry.analyze_pattern_evolution()
        analysis = {}

        for pattern_evolution in evolution_data:
            pattern_id = pattern_evolution['pattern_id']
            strength_changes = pattern_evolution['strength_changes']
            coherence_changes = pattern_evolution['coherence_changes']

            if len(strength_changes) > 1:
                # Calculate average change per step
                avg_strength_change = np.mean(np.diff([s[1] for s in strength_changes]))
                avg_coherence_change = np.mean(np.diff([c[1] for c in coherence_changes]))
                
                analysis[pattern_id] = {
                    'avg_strength_change': avg_strength_change,
                    'avg_coherence_change': avg_coherence_change
                }

        return analysis
    
    @staticmethod
    def detect_anomalies(patterns: list, threshold: float) -> list:
      """
      Detect anomalies in patterns based on a given threshold.
      Anomalies are defined as patterns whose strength or coherence is 
      significantly different from the average.
      """
      strengths = [pattern.get('strength', 0) for pattern in patterns]
      coherences = [pattern.get('coherence', 0) for pattern in patterns]
      
      avg_strength = np.mean(strengths)
      std_strength = np.std(strengths)
      avg_coherence = np.mean(coherences)
      std_coherence = np.std(coherences)
      
      anomalies = []
      for pattern in patterns:
          is_anomalous = False
          reason = ""

          # Check for strength anomalies
          if abs(pattern.get('strength', 0) - avg_strength) > threshold * std_strength:
              is_anomalous = True
              reason += f"Strength anomaly (strength={pattern.get('strength', 0):.2f}, avg={avg_strength:.2f}, std={std_strength:.2f}); "

          # Check for coherence anomalies
          if abs(pattern.get('coherence', 0) - avg_coherence) > threshold * std_coherence:
              is_anomalous = True
              reason += f"Coherence anomaly (coherence={pattern.get('coherence', 0):.2f}, avg={avg_coherence:.2f}, std={std_coherence:.2f}); "

          if is_anomalous:
              anomalies.append({
                  'pattern': pattern,
                  'reason': reason.strip()
              })
              
      return anomalies
