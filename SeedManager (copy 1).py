import random

class SeedManager:
    """
    Handles genetic traits and replication logic for nodes in the Kaleidoscope AI system.
    Responsible for creating, mutating, and initializing node seeds.
    """

    @staticmethod
    def generate_seed(base_traits: dict, mutation_rate: float = 0.1) -> dict:
        """
        Generates a new seed by applying mutations to base traits.
        :param base_traits: Dictionary of base traits to inherit.
        :param mutation_rate: Probability of mutating each trait.
        :return: New traits dictionary for the replicated node.
        """
        new_traits = base_traits.copy()

        for trait, value in base_traits.items():
            if isinstance(value, (int, float)) and random.random() < mutation_rate:
                mutation_factor = random.uniform(0.9, 1.1)  # Small mutation
                new_traits[trait] = value * mutation_factor

        return new_traits

    @staticmethod
    def initialize_node(node_id: str, seed: dict) -> dict:
        """
        Initializes a node's state from its genetic seed.
        :param node_id: Unique identifier for the node.
        :param seed: Dictionary containing the node's traits.
        :return: Initialized node attributes.
        """
        node_attributes = {
            "id": node_id,
            "traits": seed,
            "energy": seed.get("energy", 100),
            "status": "active",
            "tasks": []
        }
        print(f"Node '{node_id}' initialized with attributes: {node_attributes}")
        return node_attributes

    @staticmethod
    def evaluate_traits(traits: dict, performance_metrics: dict) -> dict:
        """
        Adjusts traits based on performance metrics.
        :param traits: Current traits of the node.
        :param performance_metrics: Dictionary of performance metrics to evaluate.
        :return: Updated traits.
        """
        for metric, impact in performance_metrics.items():
            if metric in traits and isinstance(traits[metric], (int, float)):
                traits[metric] += impact

        return traits

# Example usage
if __name__ == "__main__":
    base_traits = {
        "energy": 100,
        "learning_rate": 0.05,
        "adaptability": 0.8
    }

    # Generate a new seed with mutations
    new_seed = SeedManager.generate_seed(base_traits, mutation_rate=0.2)
    print("Generated Seed:", new_seed)

    # Initialize a node with the new seed
    node_attributes = SeedManager.initialize_node("Node1", new_seed)

    # Evaluate traits based on performance
    performance_metrics = {"energy": -10, "learning_rate": 0.01}
    updated_traits = SeedManager.evaluate_traits(node_attributes["traits"], performance_metrics)
    print("Updated Traits:", updated_traits)
