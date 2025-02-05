from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import networkx as nx
import numpy as np
from collections import defaultdict

@dataclass
class MemoryState:
    """Represents the current state of a memory bank."""
    bank_id: str
    capacity: int = 100
    current_load: int = 0
    connections: Dict[str, float] = field(default_factory=dict)
    strength: float = 1.0
    last_access: datetime = field(default_factory=datetime.now)
    evolution_stage: int = 0

class MemoryEvolution:
    """Manages the evolution and optimization of memory banks."""
    
    def __init__(self):
        self.memory_network = nx.DiGraph()
        self.bank_states = {}
        self.pattern_strengths = defaultdict(float)
        self.insight_cache = {}
        self.evolution_history = []
        
    def optimize_memory(self, insights: List[Dict[str, Any]]):
        """Optimizes memory structure based on new insights."""
        # Record current state
        current_state = self._capture_state()
        
        # Strengthen important connections
        self._strengthen_connections(insights)
        
        # Evolve memory structure
        self._evolve_structure()
        
        # Prune weak connections
        self._prune_weak_connections()
        
        # Record evolution
        self._record_evolution(current_state)
        
    def _capture_state(self) -> Dict[str, Any]:
        """Captures current state of memory network."""
        return {
            'timestamp': datetime.now().isoformat(),
            'num_banks': len(self.bank_states),
            'total_connections': self.memory_network.number_of_edges(),
            'bank_loads': {
                bank_id: state.current_load / state.capacity
                for bank_id, state in self.bank_states.items()
            },
            'network_density': nx.density(self.memory_network)
        }
        
    def _strengthen_connections(self, insights: List[Dict[str, Any]]):
        """Strengthens connections based on insights."""
        for insight in insights:
            # Get related patterns
            patterns = insight.get('patterns', [])
            
            # Strengthen pattern connections
            for i, pattern1 in enumerate(patterns):
                for pattern2 in patterns[i+1:]:
                    self._update_connection_strength(
                        pattern1['id'],
                        pattern2['id'],
                        insight['confidence']
                    )
                    
            # Update pattern strengths
            for pattern in patterns:
                self.pattern_strengths[pattern['id']] += insight['confidence']
                
    def _update_connection_strength(self, source: str, target: str, confidence: float):
        """Updates strength of connection between two patterns."""
        if self.memory_network.has_edge(source, target):
            current_weight = self.memory_network.edges[source, target]['weight']
            new_weight = (current_weight * 0.9) + (confidence * 0.1)
            self.memory_network.edges[source, target]['weight'] = new_weight
        else:
            self.memory_network.add_edge(source, target, weight=confidence)
            
    def _evolve_structure(self):
        """Evolves memory structure based on current state."""
        for bank_id, state in self.bank_states.items():
            # Check if bank needs evolution
            if self._should_evolve(state):
                self._evolve_bank(bank_id)
                
    def _should_evolve(self, state: MemoryState) -> bool:
        """Determines if a memory bank should evolve."""
        conditions = [
            state.current_load / state.capacity > 0.9,  # High load
            len(state.connections) > 10,  # Sufficient connections
            state.strength > 0.7  # Strong patterns
        ]
        return all(conditions)
        
    def _evolve_bank(self, bank_id: str):
        """Evolves a single memory bank."""
        state = self.bank_states[bank_id]
        
        # Increase capacity
        state.capacity = int(state.capacity * 1.5)
        
        # Strengthen connections
        for target, strength in state.connections.items():
            state.connections[target] = min(1.0, strength * 1.1)
            
        # Update evolution stage
        state.evolution_stage += 1
        
        self._record_bank_evolution(bank_id)
        
    def _prune_weak_connections(self, threshold: float = 0.3):
        """Removes weak connections from memory network."""
        edges_to_remove = [
            (u, v)
            for u, v, data in self.memory_network.edges(data=True)
            if data['weight'] < threshold
        ]
        
        self.memory_network.remove_edges_from(edges_to_remove)
        
    def _record_evolution(self, previous_state: Dict[str, Any]):
        """Records evolution event."""
        current_state = self._capture_state()
        
        evolution_event = {
            'timestamp': datetime.now().isoformat(),
            'previous_state': previous_state,
            'current_state': current_state,
            'changes': {
                'banks_evolved': sum(
                    1 for state in self.bank_states.values()
                    if state.evolution_stage > 0
                ),
                'connections_pruned': (
                    previous_state['total_connections'] - 
                    current_state['total_connections']
                ),
                'network_density_change': (
                    current_state['network_density'] - 
                    previous_state['network_density']
                )
            }
        }
        
        self.evolution_history.append(evolution_event)
        
    def _record_bank_evolution(self, bank_id: str):
        """Records evolution of a specific memory bank."""
        state = self.bank_states[bank_id]
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'bank_id': bank_id,
            'evolution_stage': state.evolution_stage,
            'new_capacity': state.capacity,
            'connection_count': len(state.connections),
            'strength': state.strength
        }
        
        self.evolution_history.append(event)
        
    def get_evolution_metrics(self) -> Dict[str, Any]:
        """Returns metrics about memory evolution."""
        if not self.evolution_history:
            return {}
            
        recent_events = self.evolution_history[-10:]
        
        return {
            'total_evolutions': len(self.evolution_history),
            'evolved_banks': len([
                state for state in self.bank_states.values()
                if state.evolution_stage > 0
            ]),
            'average_bank_strength': np.mean([
                state.strength for state in self.bank_states.values()
            ]),
            'network_metrics': {
                'density': nx.density(self.memory_network),
                'avg_clustering': nx.average_clustering(self.memory_network),
                'strong_connections': sum(
                    1 for _, _, data in self.memory_network.edges(data=True)
                    if data['weight'] > 0.7
                )
            },
            'recent_evolution_rate': sum(
                1 if 'evolution_stage' in event else 0
                for event in recent_events
            ) / len(recent_events)
        }
