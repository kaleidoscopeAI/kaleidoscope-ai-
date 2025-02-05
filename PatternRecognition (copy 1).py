import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from scipy.signal import find_peaks
from typing import List, Dict

class PatternRecognition:
    """
    Extracts patterns from text, numerical, and visual data.
    """

    def __init__(self):
        self.text_vectorizer = TfidfVectorizer(stop_words='english')
        self.numerical_pca = PCA(n_components=2)  # For dimensionality reduction

    def extract_text_patterns(self, corpus: List[str]) -> Dict:
        """
        Extracts significant patterns from a corpus of text.
        :param corpus: List of text strings.
        :return: Dictionary of extracted features and their importance scores.
        """
        tfidf_matrix = self.text_vectorizer.fit_transform(corpus).toarray()
        feature_names = self.text_vectorizer.get_feature_names_out()
        feature_scores = np.sum(tfidf_matrix, axis=0)

        return {
            "features": feature_names.tolist(),
            "scores": feature_scores.tolist()
        }

    def detect_numerical_patterns(self, data: np.ndarray) -> Dict:
        """
        Analyzes numerical data to detect trends and peaks.
        :param data: Numpy array of numerical data.
        :return: Dictionary of identified trends and peaks.
        """
        # Dimensionality reduction
        reduced_data = self.numerical_pca.fit_transform(data)

        # Detect peaks in each dimension
        peaks = {}
        for dim in range(reduced_data.shape[1]):
            peak_indices, _ = find_peaks(reduced_data[:, dim], height=0)
            peaks[f"dimension_{dim}"] = peak_indices.tolist()

        return {
            "reduced_data": reduced_data.tolist(),
            "peaks": peaks
        }

    def combine_insights(self, text_data: List[str], numerical_data: np.ndarray) -> Dict:
        """
        Combines insights from text and numerical data for cross-domain analysis.
        :param text_data: List of text strings.
        :param numerical_data: Numpy array of numerical data.
        :return: Dictionary of combined insights.
        """
        text_insights = self.extract_text_patterns(text_data)
        numerical_insights = self.detect_numerical_patterns(numerical_data)

        return {
            "text_insights": text_insights,
            "numerical_insights": numerical_insights
        }

# Example usage
if __name__ == "__main__":
    pr = PatternRecognition()

    # Text pattern recognition
    text_data = ["The AI system is revolutionary.", "This system learns dynamically.", "Patterns emerge naturally."]
    text_patterns = pr.extract_text_patterns(text_data)
    print("Text Patterns:", text_patterns)

    # Numerical pattern recognition
    numerical_data = np.random.rand(100, 3)  # 100 samples, 3 dimensions
    numerical_patterns = pr.detect_numerical_patterns(numerical_data)
    print("Numerical Patterns:", numerical_patterns)

    # Combined insights
    combined = pr.combine_insights(text_data, numerical_data)
    print("Combined Insights:", combined)
