memory/banks.py
Python

import numpy as np

class MemoryBank:
    def __init__(self, capacity: int, dimensions: int):
        self.capacity = capacity
        self.dimensions = dimensions
        self.data = np.zeros((capacity, dimensions), dtype=np.complex128)
        self.head = 0  # Pointer to the next available memory slot

    def store(self, data_vector: np.ndarray):
        """Store a data vector in the memory bank."""
        if data_vector.shape[0] != self.dimensions:
            raise ValueError("Data vector dimensions do not match memory bank dimensions.")

        self.data[self.head] = data_vector
        self.head = (self.head + 1) % self.capacity

    def retrieve(self, index: int) -> np.ndarray:
        """Retrieve a data vector from a specific index in the memory bank."""
        if index < 0 or index >= self.capacity:
            raise IndexError("Index out of range.")

        return self.data[index]

    def get_recent(self, n: int) -> np.ndarray:
        """Retrieve the n most recently stored data vectors."""
        if n > self.capacity:
            raise ValueError("Cannot retrieve more elements than the capacity of the memory bank.")

        start = (self.head - n) % self.capacity
        if start < self.head:
            return self.data[start:self.head]
        else:
            return np.concatenate((self.data[start:], self.data[:self.head]))
    
    def get_state(self) -> dict:
      """Return the current state of the memory bank."""
      return {
          'capacity': self.capacity,
          'dimensions': self.dimensions,
          'head': self.head,
          'fill_level': min(self.head + 1, self.capacity) / self.capacity
      }
