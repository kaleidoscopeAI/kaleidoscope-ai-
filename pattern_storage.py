memory/pattern_storage.py
Python

class PatternStorage:
    def __init__(self, max_patterns: int = 1000):
        self.max_patterns = max_patterns
        self.patterns = []
        self.pattern_count = 0

    def store_pattern(self, pattern: dict):
        """Store a pattern in the storage."""
        if self.pattern_count < self.max_patterns:
            self.patterns.append(pattern)
            self.pattern_count += 1
        else:
            # Replace the oldest pattern (FIFO)
            self.patterns.pop(0)
            self.patterns.append(pattern)

    def retrieve_similar_patterns(self, pattern: dict, threshold: float) -> list:
        """Retrieve patterns similar to the given pattern based on a similarity threshold."""
        similar_patterns = []
        for stored_pattern in self.patterns:
            similarity = self._calculate_similarity(pattern, stored_pattern)
            if similarity >= threshold:
                similar_patterns.append(stored_pattern)
        return similar_patterns

    def _calculate_similarity(self, pattern1: dict, pattern2: dict) -> float:
        """Calculate the similarity between two patterns."""
        # Example similarity metric: cosine similarity of pattern features
        features1 = self._extract_features(pattern1)
        features2 = self._extract_features(pattern2)

        # Ensure features are of the same length
        min_len = min(len(features1), len(features2))
        features1 = features1[:min_len]
        features2 = features2[:min_len]
        
        if np.all(features1 == 0) or np.all(features2 == 0):
          return 0.0 # Avoid division by zero

        dot_product = np.dot(features1, features2)
        magnitude1 = np.linalg.norm(features1)
        magnitude2 = np.linalg.norm(features2)

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0  # Avoid division by zero

        return dot_product / (magnitude1 * magnitude2)

    def _extract_features(self, pattern: dict) -> np.ndarray:
        """Extract features from a pattern for similarity comparison."""
        # Example: extract magnitude and phase as features
        features = [pattern.get('magnitude', 0), pattern.get('phase', 0)]
        
        # Add other features as needed
        if 'type' in pattern:
            # Convert pattern type to a numerical value (e.g., using a hash function)
            features.append(hash(pattern['type']) % (10**8))  # Modulo to limit the size of the hash
        
        return np.array(features)
    
    def get_state(self) -> dict:
      """Return the current state of the pattern storage."""
      return {
          'max_patterns': self.max_patterns,
          'pattern_count': self.pattern_count,
          'oldest_pattern_timestamp': self.patterns[0]['timestamp'] if self.patterns else None
      }
