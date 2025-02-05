from __future__ import annotations
import numpy as np
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import logging
from datetime import datetime

from .structure import DNASequence
from .traits import TraitManager

logger = logging.getLogger(__name__)

@dataclass
class MutationProfile:
    """Defines mutation characteristics for DNA evolution."""
    base_rate: float
    trait_weights: Dict[str, float]
    stability_factor: float
    adaptive_pressure: float
    generation: int
    mutation_history: List[Dict] = field(default_factory=list)

class DNAMutator:
    """Handles DNA mutation and evolution mechanics."""
    
    def __init__(self, trait_manager: TraitManager):
        self.trait_manager = trait_manager
        self.mutation_profiles: Dict[str, MutationProfile] = {}
        
    async def mutate_sequence(
        self,
        sequence: DNASequence,
        pressure: float = 1.0
    ) -> DNASequence:
        profile = self._create_mutation_profile(sequence, pressure)
        mutated_traits = {}
        
        for trait, value in sequence.traits.items():
            if self._should_mutate(trait, profile):
                new_value = self._mutate_trait(
                    trait,
                    value,
                    profile
                )
                mutated_traits[trait] = new_value
            else:
                mutated_traits[trait] = value
                
        return DNASequence(
            sequence_id=f"{sequence.sequence_id}_m{profile.generation}",
            traits=mutated_traits,
            generation=profile.generation,
            parent_id=sequence.sequence_id
        )

    def _create_mutation_profile(
        self,
        sequence: DNASequence,
        pressure: float
    ) -> MutationProfile:
        """Creates mutation profile based on sequence state and pressure."""
        return MutationProfile(
            base_rate=0.01 * pressure,
            trait_weights=self._calculate_trait_weights(sequence),
            stability_factor=sequence.stability_factor,
            adaptive_pressure=pressure,
            generation=sequence.generation + 1
        )

    def _calculate_trait_weights(
        self,
        sequence: DNASequence
    ) -> Dict[str, float]:
        """Calculates weights for trait mutation probability."""
        weights = {}
        for trait, value in sequence.traits.items():
            trait_info = self.trait_manager.traits.get(trait)
            if trait_info:
                weights[trait] = (
                    trait_info.plasticity *
                    (1.0 - trait_info.adaptation_score)
                )
        return weights

    def _should_mutate(self, trait: str, profile: MutationProfile) -> bool:
        """Determines if a trait should mutate."""
        mutation_chance = (
            profile.base_rate *
            profile.trait_weights.get(trait, 1.0) *
            profile.adaptive_pressure
        )
        return np.random.random() < mutation_chance

    def _mutate_trait(
        self,
        trait: str,
        value: float,
        profile: MutationProfile
    ) -> float:
        """Applies mutation to a trait value."""
        trait_info = self.trait_manager.traits.get(trait)
        if not trait_info:
            return value

        # Calculate mutation magnitude
        magnitude = (
            np.random.normal(0, 0.1) *
            profile.adaptive_pressure *
            trait_info.plasticity
        )
        
        # Apply stability factor
        magnitude *= (1.0 - profile.stability_factor)
        
        # Calculate new value
        new_value = np.clip(
            value + magnitude,
            trait_info.min_value,
            trait_info.max_value
        )
        
        return new_value

    def record_mutation(
        self,
        sequence_id: str,
        profile: MutationProfile,
        mutations: Dict[str, float]
    ):
        """Records mutation event for analysis."""
        profile.mutation_history.append({
            "timestamp": datetime.now().isoformat(),
            "sequence_id": sequence_id,
            "mutations": mutations,
            "pressure": profile.adaptive_pressure
        })
        self.mutation_profiles[sequence_id] = profile