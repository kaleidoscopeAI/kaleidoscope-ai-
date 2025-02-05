utils/system_helpers.py
Python

import numpy as np

class SystemHelpers:

    @staticmethod
    def normalize_data(data: np.ndarray) -> np.ndarray:
        """Normalize data to a range between 0 and 1."""
        min_val = np.min(data)
        max_val = np.max(data)
        if max_val - min_val == 0:
            return np.zeros_like(data)
        return (data - min_val) / (max_val - min_val)

    @staticmethod
    def scale_data(data: np.ndarray, new_min: float, new_max: float) -> np.ndarray:
        """Scale data to a new range."""
        min_val = np.min(data)
        max_val = np.max(data)
        if max_val - min_val == 0:
          return np.full_like(data, new_min)
        scaled_data = (data - min_val) / (max_val - min_val)  # Normalize to 0-1
        return scaled_data * (new_max - new_min) + new_min  # Scale to new range

    @staticmethod
    def apply_fft(data: np.ndarray) -> np.ndarray:
        """Apply Fast Fourier Transform to the data."""
        return np.fft.fft(data)

    @staticmethod
    def apply_inverse_fft(data: np.ndarray) -> np.ndarray:
        """Apply Inverse Fast Fourier Transform to the data."""
        return np.fft.ifft(data)

    @staticmethod
    def calculate_cross_correlation(data1: np.ndarray, data2: np.ndarray) -> np.ndarray:
        """Calculate the cross-correlation between two data sets."""
        return np.correlate(data1, data2, mode='full')
    
    @staticmethod
    def detect_outliers(data: np.ndarray, threshold: float = 3.0) -> list:
      """
      Detect outliers in the data using z-score.
      
      Args:
          data: Input data as a NumPy array.
          threshold: Z-score threshold for outlier detection.
          
      Returns:
          A list of indices where outliers are detected.
      """
      z_scores = np.abs((data - np.mean(data)) / np.std(data))
      outlier_indices = np.where(z_scores > threshold)[0]
      return outlier_indices.tolist()
