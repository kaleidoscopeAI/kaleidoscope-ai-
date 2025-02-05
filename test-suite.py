# tests/test_system.py
import unittest
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from system_integration import KaleidoscopeSystem
from specialized.advanced_features import QuantumStateEngine, ResonancePatternAnalyzer
from core.base import BaseNode, BaseNetwork

class TestKaleidoscopeSystem(unittest.TestCase):
    """Test suite for core system functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.system = KaleidoscopeSystem()
        self.test_data = {
            'molecules': ['CCO', 'CC(=O)O'],
            'features': [1.0, 0.8, 0.6],
            'target_properties': {
                'energy': 0.5,
                'coherence': 0.8
            }
        }

    def test_system_initialization(self):
        """Test system initialization."""
        self.assertIsNotNone(self.system.quantum_engine)
        self.assertIsNotNone(self.system.resonance_network)
        self.assertIsNotNone(self.system.control_system)
        self.assertTrue(self.system.system_state['initialized'])

    def test_quantum_analysis(self):
        """Test quantum analysis functionality."""
        results = self.system.start_analysis(self.test_data)
        self.assertIn('process_id', results)
        self.assertIn('quantum_analysis', results)
        self.assertIn('resonance_analysis', results)

    def test_error_handling(self):
        """Test system error handling."""
        bad_data = {'molecules': ['XXX'], 'features': []}
        with self.assertRaises(Exception):
            self.system.start_analysis(bad_data)

class TestQuantumFeatures(unittest.TestCase):
    """Test suite for quantum processing features."""
    
    def setUp(self):
        """Set up test environment."""
        self.quantum_engine = QuantumStateEngine()
        self.test_state = np.random.rand(8)
        self.test_state = self.test_state / np.linalg.norm(self.test_state)

    def test_state_evolution(self):
        """Test quantum state evolution."""
        evolved_states = self.quantum_engine.apply_quantum_evolution(
            self.test_state, time_steps=5
        )
        self.assertEqual(len(evolved_states), 6)  # Initial + 5 steps
        for state in evolved_states:
            self.assertAlmostEqual(np.linalg.norm(state), 1.0, places=5)

    def test_superposition_creation(self):
        """Test superposition state creation."""
        features = [0.5, 0.3, 0.2]
        state = self.quantum_engine.create_superposition_state(features)
        self.assertEqual(len(state), self.quantum_engine.dimensions)
        self.assertAlmostEqual(np.linalg.norm(state), 1.0, places=5)

class TestResonanceAnalysis(unittest.TestCase):
    """Test suite for resonance pattern analysis."""
    
    def setUp(self):
        """Set up test environment."""
        self.analyzer = ResonancePatternAnalyzer()
        self.test_state = np.random.rand(8) + 1j * np.random.rand(8)
        self.test_state = self.test_state / np.linalg.norm(self.test_state)

    def test_pattern_analysis(self):
        """Test pattern analysis functionality."""
        results = self.analyzer.analyze_pattern(self.test_state)
        self.assertIn('coherence', results)
        self.assertIn('purity', results)
        self.assertIn('dominant_patterns', results)
        self.assertGreaterEqual(results['coherence'], 0.0)
        self.assertLessEqual(results['coherence'], 1.0)

    def test_pattern_comparison(self):
        """Test pattern comparison functionality."""
        state2 = np.random.rand(8) + 1j * np.random.rand(8)
        state2 = state2 / np.linalg.norm(state2)
        
        pattern1 = self.analyzer.analyze_pattern(self.test_state)
        pattern2 = self.analyzer.analyze_pattern(state2)
        
        similarity = self.analyzer.compare_patterns(pattern1, pattern2)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)

def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestKaleidoscopeSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestQuantumFeatures))
    suite.addTests(loader.loadTestsFromTestCase(TestResonanceAnalysis))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == '__main__':
    run_tests()
