
import unittest
import sys
import os

# Add the Unified_AI_Core directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from core.AI_Core import AICore

class TestAICoreIntegration(unittest.TestCase):
    def setUp(self):
        """Set up the AI Core for testing."""
        self.ai_core = AICore()
        self.ai_core.initialize()

    def test_node_manager(self):
        """Test that nodes are loaded correctly."""
        self.assertGreater(len(self.ai_core.node_manager.nodes), 0)
        print("Node Manager Test Passed.")

    def test_perspective_manager(self):
        """Test perspective processing with sample data."""
        sample_data = "Kaleidoscope Test"
        results = self.ai_core.perspective_manager.process_perspectives(sample_data)
        self.assertIn("Reverse Perspective", results)
        self.assertEqual(results["Reverse Perspective"], sample_data[::-1])
        print("Perspective Manager Test Passed.")

    def test_seed_manager(self):
        """Test seed generation and initialization."""
        seed = self.ai_core.seed_manager.generate_seed("TestSeed", {"type": "Processor", "version": 2.0})
        self.assertEqual(seed["parameters"]["type"], "Processor")
        initialized = self.ai_core.seed_manager.initialize_from_seed("TestSeed")
        self.assertIn("initialized_data", initialized)
        print("Seed Manager Test Passed.")

    def test_mirrored_network(self):
        """Test synchronization of mirrored networks."""
        self.ai_core.mirrored_network.sync_networks()
        for node_name in self.ai_core.mirrored_network.primary_network:
            primary_data = self.ai_core.mirrored_network.primary_network[node_name]["data"]
            secondary_data = self.ai_core.mirrored_network.secondary_network[node_name]["data"]
            self.assertEqual(primary_data, secondary_data)
        print("Mirrored Network Test Passed.")

if __name__ == "__main__":
    unittest.main()
