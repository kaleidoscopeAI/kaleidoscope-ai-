system/tests/unit/test_quantum_engine.py
Python

import unittest
import numpy as np
from kaleidoscope.core.quantum_engine import QuantumEngine

class TestQuantumEngine(unittest.TestCase):

    def setUp(self):
        self.dimensions = 4
        self.banks_per_dimension = 2
        self.engine = QuantumEngine(self.dimensions, self.banks_per_dimension)

    def test_initialization(self):
        self.assertEqual(self.engine.dimensions, self.dimensions)
        self.assertEqual(self.engine.banks_per_dimension, self.banks_per_dimension)
        self.assertEqual(self.engine.quantum_states.shape, (self.dimensions, self.banks_per_dimension))
        self.assertEqual(len(self.engine.entanglement_graph.nodes), self.dimensions)

    def test_apply_quantum_transformations(self):
        data = np.random.rand(self.dimensions, self.banks_per_dimension)
        transformed_data = self.engine._apply_quantum_transformations(data)
        self.assertEqual(transformed_data.shape, data.shape)
        self.assertTrue(np.all(transformed_data.dtype == np.complex128))

    def test_hadamard_transform(self):
        state = 0.5 + 0.5j  # Example state
        transformed_state = self.engine._hadamard_transform(state)
        # Check if the transformation is approximately correct
        expected_state = (0.5 + 0.5j) / np.sqrt(2) + (0.5 - 0.5j) / np.sqrt(2)
        self.assertAlmostEqual(transformed_state, expected_state)

    def test_apply_phase_rotation(self):
        state = 0.5 + 0.5j  # Example state
        dim = 0
        # Add a neighbor to create entanglement
        self.engine.entanglement_graph.add_edge(dim, 1)
        self.engine.resonance_matrix[dim, 1] = 0.5 + 0.5j
        rotated_state = self.engine._apply_phase_rotation(state, dim)
        self.assertNotEqual(rotated_state, state)  # State should change due to phase rotation

    def test_calculate_resonance(self):
        data = np.random.rand(self.dimensions, self.banks_per_dimension) + 1j * np.random.rand(self.dimensions, self.banks_per_dimension)
        resonance_effects = self.engine._calculate_resonance(data)
        self.assertEqual(resonance_effects.shape, data.shape)
        self.assertTrue(np.all(resonance_effects.dtype == np.complex128))
    
    def test_get_quantum_state_metrics(self):
        metrics = self.engine.get_quantum_state_metrics()
        self.assertIn('entanglement_entropy', metrics)
        self.assertIn('average_resonance', metrics)
        self.assertIn('state_purity', metrics)
        self.assertTrue(isinstance(metrics['entanglement_entropy'], float))
        self.assertTrue(isinstance(metrics['average_resonance'], float))
        self.assertTrue(isinstance(metrics['state_purity'], float))

    def test_update_entanglement(self):
        # Initially, there should be some entanglement
        initial_edges = self.engine.entanglement_graph.number_of_edges()
        
        # Set a high resonance value to ensure entanglement
        self.engine.resonance_matrix.fill(1.0 + 1.0j)
        self.engine.update_entanglement(threshold=0.5)
        edges_after_high_resonance = self.engine.entanglement_graph.number_of_edges()
        self.assertGreater(edges_after_high_resonance, initial_edges)

        # Set a low resonance value to remove entanglement
        self.engine.resonance_matrix.fill(0.0 + 0.0j)
        self.engine.update_entanglement(threshold=0.5)
        edges_after_low_resonance = self.engine.entanglement_graph.number_of_edges()
        self.assertEqual(edges_after_low_resonance, 0)
    
if __name__ == '__main__':
    unittest.main()
