from typing import Dict, List, Optional, Set
import networkx as nx
import numpy as np
import logging
from collections import defaultdict

# Import existing classes
from living_node import LivingNode
from node_dna_module import NodeDNA
from cube_processor import CubeProcessor
from node_neuralcore_module import NeuralCore

class BioCell:
    """New biological cell structure that works with existing nodes"""
    def __init__(self, node_id: str, capacity: int, energy_manager):
        # Create instance of your existing LivingNode
        self.core_node = LivingNode(node_id, capacity, energy_manager)
        
        # New biological components
        self.membrane = BiologicalMembrane()
        self.organelles = {
            "mitochondria": Mitochondria(),
            "nucleus": Nucleus(self.core_node.dna),
            "golgi": GolgiApparatus()
        }
        
        # Enhanced data processing
        self.protein_factory = ProteinFactory(self.core_node.cube_processor)
        self.metabolic_network = nx.DiGraph()

    def process_data(self, data: Dict):
        """Process data through both biological and existing systems"""
        # Filter through membrane
        filtered_data = self.membrane.filter_data(data)
        
        # Use your existing CubeProcessor through core node
        sliced_data = self.core_node.cube_processor.slice_data(
            [filtered_data], 
            "value"
        )
        
        # Process through biological systems
        proteins = self.protein_factory.synthesize(filtered_data)
        self.organelles["golgi"].process_proteins(proteins)
        
        # Use your existing node processing
        self.core_node.ingest_data([filtered_data])
        
        # Update metabolic network
        self._update_metabolism(filtered_data)
        
        return {
            "processed_data": filtered_data,
            "proteins": proteins,
            "insights": self.core_node.insight_storage
        }

    def _update_metabolism(self, data: Dict):
        """Update metabolic network based on data processing"""
        for key, value in data.items():
            if isinstance(value, (int, float)):
                self.metabolic_network.add_node(
                    key, 
                    energy_cost=abs(value) * 0.1
                )
                
        # Calculate energy requirements
        total_cost = sum(
            d["energy_cost"] 
            for _, d in self.metabolic_network.nodes(data=True)
        )
        self.organelles["mitochondria"].produce_energy(total_cost)

class BiologicalMembrane:
    """Controls what enters and exits the cell"""
    def __init__(self):
        self.permeability = 0.7
        self.channels = defaultdict(float)
        self.proteins = set()

    def filter_data(self, data: Dict) -> Dict:
        """Filter incoming data based on membrane properties"""
        filtered = {}
        for key, value in data.items():
            if self._can_pass(key, value):
                filtered[key] = value
                self.channels[key] += 0.1  # Channel adapts
        return filtered

    def _can_pass(self, key: str, value: Any) -> bool:
        """Determine if data can pass through membrane"""
        if key in self.proteins:
            return True
        return random.random() < self.permeability

class Nucleus:
    """Manages DNA and transcription"""
    def __init__(self, dna: NodeDNA):
        self.dna = dna
        self.transcription_factors = set()
        self.active_genes = set()

    def transcribe(self, signal: Dict) -> List[str]:
        """Transcribe DNA based on signal"""
        transcripts = []
        for key, value in signal.items():
            if self._is_gene_active(key):
                transcript = self._create_transcript(key, value)
                transcripts.append(transcript)
        return transcripts

    def _is_gene_active(self, gene: str) -> bool:
        """Check if gene is active"""
        return (
            gene in self.active_genes or
            random.random() < self.dna.traits.get("activation_rate", 0.5)
        )

class ProteinFactory:
    """Creates proteins (data transformers) using CubeProcessor"""
    def __init__(self, cube_processor: CubeProcessor):
        self.cube_processor = cube_processor
        self.protein_templates = {}

    def synthesize(self, data: Dict) -> List[Dict]:
        """Synthesize proteins based on data"""
        proteins = []
        
        # Use your CubeProcessor for feature analysis
        features = self.cube_processor.prioritize_features([data])
        
        for feature in features:
            if feature in data:
                protein = {
                    "type": "enzyme",
                    "target": feature,
                    "strength": self.cube_processor.aggregate_data(
                        [data], 
                        feature
                    )
                }
                proteins.append(protein)
                
        return proteins

class Mitochondria:
    """Energy production center"""
    def __init__(self):
        self.atp_level = 100.0
        self.efficiency = 0.8

    def produce_energy(self, required: float):
        """Produce energy based on requirement"""
        production = required * self.efficiency
        self.atp_level = max(0, self.atp_level - production)
        return production

class GolgiApparatus:
    """Processes and modifies proteins"""
    def __init__(self):
        self.processing_queue = []
        self.modification_rate = 0.3

    def process_proteins(self, proteins: List[Dict]):
        """Process and modify proteins"""
        for protein in proteins:
            if random.random() < self.modification_rate:
                protein["modified"] = True
                protein["strength"] *= 1.2
            self.processing_queue.append(protein)

# Example usage
if __name__ == "__main__":
    from node_energy_module import EnergyManager
    
    # Initialize components
    energy_manager = EnergyManager()
    
    # Create bio-hybrid cell
    cell = BioCell("hybrid_cell_1", capacity=100, energy_manager=energy_manager)
    
    # Test data
    test_data = {
        "value": 42,
        "type": "numeric",
        "metadata": {"source": "sensor"}
    }
    
    # Process through hybrid system
    result = cell.process_data(test_data)
    
    print("Processed Results:", result)
    print("Core Node Insights:", cell.core_node.dump_insights())
    print("Metabolic Network Size:", len(cell.metabolic_network))
