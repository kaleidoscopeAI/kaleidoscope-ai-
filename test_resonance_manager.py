system/tests/unit/test_resonance_manager.py
Python

import unittest
import numpy as np
from kaleidoscope.core.resonance_manager import ResonanceManager

class TestResonanceManager(unittest.TestCase):

    def setUp(self):
        self.dimensions = 3
        self.manager = ResonanceManager(self.dimensions)

    def test_initialization(self):
        self.assertEqual(self.manager.dimensions, self.dimensions)
        self.assertEqual(self.manager.resonance_fields.shape, (self.dimensions, 360))
        self.assertEqual(len(self.manager.resonance_graph.nodes), self.dimensions)

    def test_update_resonance_fields(self):
        data = np.random.rand(self.dimensions, 360) + 1j * np.random.rand(self.dimensions, 360)
        self.manager.update_resonance_fields(data)
        for dim in range(self.dimensions):
            self.assertTrue(np.allclose(self.manager.resonance_fields[dim], self.manager._calculate_resonance_field(data[dim], dim)))

    def test_calculate_resonance_field(self):
        data = np.random.rand(360) + 1j * np.random.rand(360)
        dim = 0
        field = self.manager._calculate_resonance_field(data, dim)
        self.assertEqual(field.shape, (360,))
        self.assertTrue(np.all(field.dtype == np.complex128))

    def test_analyze_resonance_patterns(self):
        # Create a known pattern in the resonance field
        field = np.zeros(360, dtype=np.complex128)
        field[45] = 10 + 0j  # Strong peak at 45 degrees
        self.manager.resonance_fields[0] = field

        patterns = self.manager.analyze_resonance_patterns()
        self.assertTrue(any(p['angle'] == 45 and p['dimension'] == 0 for p in patterns))

    def test_find_peaks(self):
        field = np.zeros(360, dtype=np.complex128)
        field[30] = 5 + 0j
        field[180] = 10 + 0j
        peaks = self.manager._find_peaks(field)
        peak_angles = [peak['angle'] for peak in peaks]
        self.assertIn(30, peak_angles)
        self.assertIn(180, peak_angles)

    def test_update_resonance_graph(self):
        # Create some artificial patterns
        patterns = [
            {'dimension': 0, 'angle': 30, 'magnitude': 1, 'phase': 0},
            {'dimension': 1, 'angle': 30, 'magnitude': 0.9, 'phase': 0.1}
        ]
        self.manager.update_resonance_graph(patterns)
        self.assertTrue(self.manager.resonance_graph.has_edge(0, 1))

    def test_calculate_resonance_strength(self):
        node1 = {'field': np.ones(360, dtype=np.complex128)}
        node2 = {'field': np.ones(360, dtype=np.complex128)}
        strength = self.manager._calculate_resonance_strength(node1, node2)
        self.assertAlmostEqual(strength, 1.0) 

    def test_get_resonance_metrics(self):
        metrics = self.manager.get_resonance_metrics()
        self.assertIn('average_field_strength', metrics)
        self.assertIn('resonance_connectivity', metrics)
        self.assertIn('field_entropy', metrics)
        self.assertTrue(isinstance(metrics['average_field_strength'], float))
        self.assertTrue(isinstance(metrics['resonance_connectivity'], float))
        self.assertTrue(isinstance(metrics['field_entropy'], float))

if __name__ == '__main__':
    unittest.main()
