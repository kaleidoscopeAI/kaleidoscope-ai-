from __future__ import annotations
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class DNASequence:
    """Represents a fundamental DNA sequence with traits and mutation capabilities."""
    sequence_id: str
    traits: Dict[str, float]
    generation: int
    parent_id: Optional[str] = None
    mutation_rate: float = 0.01
    stability_factor: float = 0.95
    evolution_history: List[Dict] = None

    def __post_init__(self):
        self.evolution_history = self.evolution_history or []
        self._validate_traits()
        self._initialize_weights()

    def _validate_traits(self) -> None:
        """Validates that all required traits are present with appropriate values."""
        required_traits = {
            "learning_rate": (0.0, 1.0),
            "energy_efficiency": (0.5, 2.0),
            "processing_speed": (0.1, 5.0),
            "memory_capacity": (1.0, 10.0),
            "adaptation_rate": (0.0, 1.0),
            "stability": (0.0, 1.0),
            "specialization": (0.0, 1.0)
        }

        for trait, (min_val, max_val) in required_traits.items():
            if trait not in self.traits:
                self.traits[trait] = np.random.uniform(min_val, max_val)
            else:
                self.traits[trait] = np.clip(self.traits[trait], min_val, max_val)

    def _initialize_weights(self) -> None:
        """Initializes internal weights for trait interactions."""
        self._trait_weights = {
            ("learning_rate", "adaptation_rate"): 0.8,
            ("energy_efficiency", "processing_speed"): 0.6,
            ("memory_capacity", "specialization"): 0.7,
            ("stability", "adaptation_rate"): -0.4
        }

    def mutate(self, environmental_pressure: float = 1.0) -> DNASequence:
        """
        Creates a mutated copy of the DNA sequence.
        
        Args:
            environmental_pressure: Factor influencing mutation intensity (0.0-2.0)
            
        Returns:
            New DNASequence with mutated traits
        """
        mutated_traits = {}
        mutation_record = {
            "generation": self.generation + 1,
            "parent_id": self.sequence_id,
            "mutations": {}
        }

        # Calculate adaptive mutation rate based on environmental pressure
        adaptive_rate = self.mutation_rate * environmental_pressure
        
        for trait, value in self.traits.items():
            # Calculate trait-specific mutation based on weights
            trait_pressure = self._calculate_trait_pressure(trait)
            trait_mutation = np.random.normal(0, adaptive_rate * trait_pressure)
            
            # Apply stability factor
            trait_mutation *= (1 - self.stability_factor)
            
            # Record significant mutations
            if abs(trait_mutation) > 0.01:
                mutation_record["mutations"][trait] = {
                    "previous": value,
                    "change": trait_mutation
                }
            
            mutated_traits[trait] = np.clip(value + trait_mutation, 0.0, 1.0)

        # Create new DNA sequence with mutated traits
        new_history = self.evolution_history + [mutation_record]
        return DNASequence(
            sequence_id=f"{self.sequence_id}_m{self.generation + 1}",
            traits=mutated_traits,
            generation=self.generation + 1,
            parent_id=self.sequence_id,
            mutation_rate=self.mutation_rate,
            stability_factor=self.stability_factor,
            evolution_history=new_history
        )

    def _calculate_trait_pressure(self, trait: str) -> float:
        """Calculates the mutation pressure on a specific trait based on weights."""
        pressure = 1.0
        for (trait1, trait2), weight in self._trait_weights.items():
            if trait in (trait1, trait2):
                other_trait = trait2 if trait == trait1 else trait1
                pressure += weight * self.traits[other_trait]
        return np.clip(pressure, 0.5, 2.0)

    def combine(self, other: DNASequence) -> DNASequence:
        """
        Combines this DNA sequence with another to produce offspring.
        
        Args:
            other: Another DNASequence to combine with
            
        Returns:
            New DNASequence with combined traits
        """
        combined_traits = {}
        combination_record = {
            "type": "combination",
            "parents": [self.sequence_id, other.sequence_id],
            "traits": {}
        }

        for trait in self.traits:
            # Use weighted average with random factor
            weight = np.random.beta(2, 2)  # Beta distribution for natural variation
            combined_value = (
                weight * self.traits[trait] +
                (1 - weight) * other.traits[trait]
            )
            
            # Add some random variation
            variation = np.random.normal(0, 0.05)
            combined_value = np.clip(combined_value + variation, 0.0, 1.0)
            
            combined_traits[trait] = combined_value
            combination_record["traits"][trait] = {
                "parent1": self.traits[trait],
                "parent2": other.traits[trait],
                "combined": combined_value
            }

        # Create new DNA sequence with combined traits
        new_history = self.evolution_history + [combination_record]
        return DNASequence(
            sequence_id=f"combined_{self.sequence_id}_{other.sequence_id}",
            traits=combined_traits,
            generation=max(self.generation, other.generation) + 1,
            parent_id=f"{self.sequence_id}+{other.sequence_id}",
            mutation_rate=(self.mutation_rate + other.mutation_rate) / 2,
            stability_factor=(self.stability_factor + other.stability_factor) / 2,
            evolution_history=new_history
        )

    def save(self, path: Union[str, Path]) -> None:
        """Saves the DNA sequence to a file."""
        data = {
            "sequence_id": self.sequence_id,
            "traits": self.traits,
            "generation": self.generation,
            "parent_id": self.parent_id,
            "mutation_rate": self.mutation_rate,
            "stability_factor": self.stability_factor,
            "evolution_history": self.evolution_history
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info(f"DNA sequence saved to {path}")

    @classmethod
    def load(cls, path: Union[str, Path]) -> DNASequence:
        """Loads a DNA sequence from a file."""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)

    def evaluate_fitness(self, environment_state: Dict[str, float]) -> float:
        """
        Evaluates the fitness of this DNA sequence in a given environment.
        
        Args:
            environment_state: Dictionary containing environmental parameters
            
        Returns:
            Fitness score (0.0-1.0)
        """
        fitness_scores = []
        
        # Evaluate each trait's contribution to fitness
        for trait, value in self.traits.items():
            if trait in environment_state:
                # Calculate how well the trait matches environmental demands
                difference = abs(value - environment_state[trait])
                trait_fitness = 1.0 - (difference / 1.0)  # Normalize to 0-1
                fitness_scores.append(trait_fitness)
        
        # Calculate overall fitness
        if fitness_scores:
            return np.mean(fitness_scores)
        return 0.0

    def analyze_evolution(self) -> Dict:
        """Analyzes the evolutionary history of the DNA sequence."""
        analysis = {
            "generations": self.generation,
            "mutation_count": 0,
            "trait_trends": {trait: [] for trait in self.traits},
            "significant_changes": []
        }

        # Analyze evolution history
        for record in self.evolution_history:
            if "mutations" in record:
                analysis["mutation_count"] += len(record["mutations"])
                for trait, change in record["mutations"].items():
                    if abs(change["change"]) > 0.1:  # Significant change threshold
                        analysis["significant_changes"].append({
                            "generation": record["generation"],
                            "trait": trait,
                            "change": change["change"]
                        })

        return analysis
