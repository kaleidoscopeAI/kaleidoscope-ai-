data_processing/historical/pattern_extractor.py
Python

import numpy as np

class PatternExtractor:
    def __init__(self, data_analyzer: DataAnalyzer):
        self.data_analyzer = data_analyzer
        self.extracted_patterns = []

    def extract_patterns(self, start_time, end_time, pattern_type: str) -> list:
        """Extract patterns of a specific type from historical data."""
        analysis_results = self.data_analyzer.analyze_historical_data(start_time, end_time)
        if not analysis_results:
            return []

        patterns = []
        if pattern_type == 'trend':
            patterns = self._extract_trends(analysis_results)
        elif pattern_type == 'anomaly':
            patterns = self._extract_anomalies(analysis_results)
        # Add more pattern types as needed

        self.extracted_patterns.extend(patterns)
        return patterns

    def _extract_trends(self, analysis_results: dict) -> list:
        """Extract trend patterns from analysis results."""
        trends = []
        for i in range(len(analysis_results['mean'])):
            # Example: Detect increasing or decreasing trends based on mean values
            if analysis_results['mean'][i] > analysis_results['mean'][0] * 1.1:  # 10% increase
                trends.append({
                    'type': 'trend',
                    'pattern': 'increasing',
                    'dimension': i,
                    'start_time': analysis_results['start_time'],
                    'end_time': analysis_results['end_time']
                })
            elif analysis_results['mean'][i] < analysis_results['mean'][0] * 0.9:  # 10% decrease
                trends.append({
                    'type': 'trend',
                    'pattern': 'decreasing',
                    'dimension': i,
                    'start_time': analysis_results['start_time'],
                    'end_time': analysis_results['end_time']
                })

        return trends

    def _extract_anomalies(self, analysis_results: dict) -> list:
      """
      Extract anomaly patterns from analysis results.
      Anomalies are data points that deviate significantly from the mean, considering the standard deviation.
      """
      anomalies = []
      data = self.data_analyzer.data_storage.retrieve_data(analysis_results['start_time'], analysis_results['end_time'])
      data_array = np.array(data)

      for i in range(data_array.shape[1]):  # Iterate over each dimension
          for j, value in enumerate(data_array[:, i]):
              # Calculate the z-score to determine how many standard deviations a data point is from the mean
              z_score = (value - analysis_results['mean'][i]) / analysis_results['std'][i] if analysis_results['std'][i] > 0
              # Consider a data point an anomaly if its z-score is above a certain threshold (e.g., 2.5)
              if abs(z_score) > 2.5:
                  anomalies.append({
                      'type': 'anomaly',
                      'dimension': i,
                      'value': value,
                      'z_score': z_score,
                      'timestamp': data[j]['timestamp'],
                      'data_index': j
                  })

      return anomalies

    def get_state(self) -> dict:
        """Returns the current state of the pattern extractor."""
        return {
            'extracted_patterns_count': len(self.extracted_patterns),
            'last_extraction': {
                'start_time': self.extracted_patterns[-1]['start_time'] if self.extracted_patterns else None,
                'end_time': self.extracted_patterns[-1]['end_time'] if self.extracted_patterns else None,
                'pattern_type': self.extracted_patterns[-1]['type'] if self.extracted_patterns else None
            }
        }
