
from core.thought_nexus import ThoughtNexus
from core.global_memory import GlobalMemory
from modules.knowledge_synchronizer import KnowledgeSynchronizer

# Example execution of the Thought Nexus and Knowledge Synchronizer
def run_thought_nexus_example():
    global_memory = GlobalMemory()
    thought_nexus = ThoughtNexus()
    synchronizer = KnowledgeSynchronizer(global_memory, thought_nexus)

    # Simulate adding node data to global memory
    global_memory.add_data(["Data from Node 1", "Data from Node 2"])

    # Synchronize and refine knowledge
    refined_knowledge = synchronizer.synchronize()
    print("Final Refined Knowledge:", refined_knowledge)

if __name__ == "__main__":
    run_thought_nexus_example()
        