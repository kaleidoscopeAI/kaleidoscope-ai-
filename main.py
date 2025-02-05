# Main script to run the AI system
from core.memory_bank import MemoryBank
from core.kaleidoscope_engine import KaleidoscopeEngine
from core.feedback_node import FeedbackIntegratedNode
from core.shared_engine import SharedEngine
from utils.visualizer import Visualizer
from utils.addiction_module import AddictionModule

def main():
    engine = KaleidoscopeEngine()
    addiction_module = AddictionModule()

    # Simulate parsing and processing data from multiple formats
    json_data = addiction_module.parse_data("sample.json")
    print("Parsed JSON:", json_data)

    node = FeedbackIntegratedNode("node_1", memory_threshold=5, kaleidoscope_engine=engine)
    node.process_data("Example data 1")
    node.process_data("Example data 2")
    print("Final output:", engine.process())

if __name__ == "__main__":
    main()
