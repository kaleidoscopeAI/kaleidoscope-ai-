from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, Counter
import numpy as np
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cosine
import time
import uuid

class OrganicNode:
    def __init__(self, genetic_code: Optional[GeneticCode] = None):
        # Inherit your existing initialization
        self.id = str(uuid.uuid4())
        self.dna = genetic_code or GeneticCode()
        self.birth_time = time.time()
        
        # Your existing knowledge structures
        self.knowledge_base: Dict[str, Knowledge] = {}
        self.truth_matrix: Dict[str, float] = defaultdict(float)
        self.contradiction_map: Dict[str, Set[str]] = defaultdict(set)
        
        # Your existing memory components
        self.energy = 10.0
        self.maturity = 0.0
        self.specialization = None
        self.connections = set()
        self.short_term_memory = []
        self.long_term_memory: Dict[str, Knowledge] = {}
        self.validation_queue = []

        # Add new bio-inspired components
        self.metabolic_rate = self.dna.traits["energy_efficiency"]
        self.cell_membrane = CellMembrane(self.dna.traits["permeability"])
        self.mitochondria = Mitochondria(self.metabolic_rate)
        
    def process_information(self, content: str, source: str) -> Dict:
        """Enhanced version of your process_information method"""
        if self.energy < 1.0:
            return {"status": "insufficient_energy"}
            
        try:
            # Use your existing methods
            facts = self._extract_facts(content)
            initial_score = self._compute_initial_truth_score(facts)
            
            # Create knowledge unit using your Knowledge class
            knowledge = Knowledge(
                content=content,
                source=source,
                timestamp=time.time(),
                truth_score=initial_score
            )
            
            # Add metabolic processing
            energy_cost = self.mitochondria.process_knowledge(knowledge)
            self.energy -= energy_cost
            
            # Use your validation system
            validation_result = self._validate_knowledge(knowledge, facts)
            self._update_truth_scores(validation_result)
            
            # Enhanced storage with membrane filtering
            if validation_result['truth_score'] > self.dna.validation_threshold:
                filtered_knowledge = self.cell_membrane.filter_knowledge(knowledge)
                self._store_knowledge(filtered_knowledge, validation_result)
            
            return {
                "status": "success",
                "truth_score": validation_result['truth_score'],
                "contradictions": validation_result['contradictions'],
                "supporting_evidence": validation_result['supporting'],
                "energy_cost": energy_cost
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def replicate(self) -> 'OrganicNode':
        """Enhanced version of your replicate method"""
        # Verify energy levels
        if self.energy < 20.0:
            return None
            
        # Create child node with mutated DNA
        child = OrganicNode(self.dna.mutate())
        
        # Transfer most reliable knowledge (from your implementation)
        reliable_knowledge = {
            k: v for k, v in self.long_term_memory.items()
            if v.truth_score > 0.9
        }
        
        # Use your sorting method
        top_knowledge = dict(sorted(
            reliable_knowledge.items(),
            key=lambda x: x[1].truth_score,
            reverse=True
        )[:10])
        
        # Update child's memory
        child.long_term_memory.update(top_knowledge)
        
        # Split energy between parent and child
        self.energy /= 2
        child.energy = self.energy
        
        return child

class CellMembrane:
    """New class to handle selective data permeability"""
    def __init__(self, permeability: float):
        self.permeability = permeability
        self.receptors = defaultdict(float)
        
    def filter_knowledge(self, knowledge: Knowledge) -> Knowledge:
        """Filter knowledge based on membrane properties"""
        # Extract key features
        features = self._extract_features(knowledge.content)
        
        # Update receptors based on content
        for feature in features:
            self.receptors[feature] += 0.1
            
        # Filter content based on receptors
        filtered_content = self._apply_filtering(knowledge.content)
        
        # Return filtered knowledge
        return Knowledge(
            content=filtered_content,
            source=knowledge.source,
            timestamp=knowledge.timestamp,
            truth_score=knowledge.truth_score
        )
        
    def _extract_features(self, content: str) -> Set[str]:
        """Extract key features from content"""
        vectorizer = TfidfVectorizer(max_features=100)
        try:
            tfidf_matrix = vectorizer.fit_transform([content])
            feature_names = vectorizer.get_feature_names()
            return set(feature_names)
        except:
            return set()
            
    def _apply_filtering(self, content: str) -> str:
        """Apply membrane filtering to content"""
        words = content.split()
        filtered_words = [
            word for word in words
            if self.receptors.get(word.lower(), 0) >= self.permeability
        ]
        return " ".join(filtered_words)

class Mitochondria:
    """New class to handle energy production and consumption"""
    def __init__(self, efficiency: float):
        self.efficiency = efficiency
        self.atp_storage = 100.0
        self.cycle_count = 0
        
    def process_knowledge(self, knowledge: Knowledge) -> float:
        """Process knowledge and return energy cost"""
        # Calculate base cost
        base_cost = len(knowledge.content) * 0.01
        
        # Apply efficiency modifier
        actual_cost = base_cost * (1 - self.efficiency)
        
        # Update ATP storage
        self.atp_storage -= actual_cost
        self.cycle_count += 1
        
        # Regenerate ATP periodically
        if self.cycle_count >= 10:
            self._regenerate_atp()
            self.cycle_count = 0
            
        return actual_cost
        
    def _regenerate_atp(self):
        """Regenerate ATP storage"""
        regeneration_amount = 10.0 * self.efficiency
        self.atp_storage = min(100.0, self.atp_storage + regeneration_amount)

# Example usage
if __name__ == "__main__":
    # Create node
    node = OrganicNode()
    
    # Test information processing
    result = node.process_information(
        content="Example content for processing",
        source="test"
    )
    print(f"Processing Result: {result}")
    
    # Test replication
    child_node = node.replicate()
    if child_node:
        print(f"Child Node Created: {child_node.id}")
        print(f"Child Energy Level: {child_node.energy}")
        print(f"Child Memory Size: {len(child_node.long_term_memory)}")
