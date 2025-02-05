utils/quantum_math.py
Python

import numpy as np
import scipy.linalg as spl

class QuantumMath:

    @staticmethod
    def create_entangled_state(num_dimensions: int) -> np.ndarray:
        """Create a maximally entangled state for a given number of dimensions."""
        state = np.zeros(2 ** num_dimensions, dtype=np.complex128)
        state[0] = 1 / np.sqrt(2)
        state[-1] = 1 / np.sqrt(2)
        return state

    @staticmethod
    def apply_hadamard(state: np.ndarray) -> np.ndarray:
        """Apply the Hadamard transformation to a given quantum state."""
        dim = int(np.log2(len(state)))  # Infer the number of qubits from state size
        hadamard_gate = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]])
        
        # Create a tensor product of Hadamard gates for the full system
        full_hadamard = hadamard_gate
        for _ in range(1, dim):
            full_hadamard = np.kron(full_hadamard, hadamard_gate)

        return np.dot(full_hadamard, state)

    @staticmethod
    def measure_state(state: np.ndarray) -> int:
        """Perform a measurement on the given quantum state."""
        probabilities = np.abs(state) ** 2
        return np.random.choice(len(state), p=probabilities)

    @staticmethod
    def calculate_density_matrix(state: np.ndarray) -> np.ndarray:
      """Calculate the density matrix for a given quantum state."""
      return np.outer(state, np.conj(state))

    @staticmethod
    def calculate_purity(state: np.ndarray) -> float:
      """Calculate the purity of a given quantum state."""
      density_matrix = QuantumMath.calculate_density_matrix(state)
      return np.real(np.trace(np.dot(density_matrix, density_matrix)))
    
    @staticmethod
    def calculate_entanglement_entropy(state: np.ndarray) -> float:
      """Calculate the entanglement entropy of a given quantum state."""
      # Assuming the state represents a bipartite system of equal size
      dim = int(len(state) ** 0.5)
      
      # Reshape the state into a matrix
      reshaped_state = state.reshape((dim, dim))

      # Perform singular value decomposition
      _, s, _ = np.linalg.svd(reshaped_state)

      # Calculate probabilities from singular values
      probabilities = s**2 / np.sum(s**2)

      # Calculate entropy
      entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
      
      return entropy

    @staticmethod
    def unitary_transform(state: np.ndarray, matrix: np.ndarray) -> np.ndarray:
      """
      Apply a unitary transformation to a quantum state.
      
      Args:
          state: The quantum state vector.
          matrix: The unitary transformation matrix.
          
      Returns:
          The transformed quantum state.
      """
      if not QuantumMath.is_unitary(matrix):
          raise ValueError("The provided matrix is not unitary.")
      
      return np.dot(matrix, state)
    
    @staticmethod
    def is_unitary(matrix: np.ndarray, tolerance: float = 1e-10) -> bool:
      """
      Check if a matrix is unitary.
      
      Args:
          matrix: The matrix to check.
          tolerance: The tolerance for checking if the matrix is unitary.
          
      Returns:
          True if the matrix is unitary, False otherwise.
      """
      
      # Calculate the conjugate transpose
      matrix_dagger = np.conj(matrix).T
      
      # Calculate the product of the matrix and its conjugate transpose
      product = np.dot(matrix, matrix_dagger)
      
      # Check if the product is close to the identity matrix
      identity = np.eye(matrix.shape[0])
      return np.allclose(product, identity, atol=tolerance)
