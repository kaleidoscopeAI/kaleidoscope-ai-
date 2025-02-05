import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import uuid
import time
from typing import Dict, List, Optional, Tuple
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import PCA
from dataclasses import dataclass
from collections import deque

@dataclass
class GrowthState:
    maturity: float = 0.0
    knowledge: float = 0.0
    specialization: Optional[str] = None

@dataclass
class Traits:
    learning_rate: float = 0.1
    adaptation_rate: float = 0.1
    energy_efficiency: float = 1.0

class Node:
    def __init__(self, node_id: Optional[str] = None):
        self.id = node_id or str(uuid.uuid4())
        self.birth_time = time.time()
        self.energy = 10.0
        self.growth_state = GrowthState()
        self.traits = Traits()
        
        # Enhanced memory systems with size limits
        self.short_term = deque(maxlen=100)  # Limited short-term memory
        self.long_term: Dict[str, Dict] = {}
        self.max_long_term = 1000
        
        self.experiences = deque(maxlen=1000)  # Limited experience history
        self.growth_path = deque(maxlen=1000)  # Limited growth tracking
        self.connections = set()
        
        # New: Adaptive learning system
        self.learning_history = deque(maxlen=100)
        self.adaptation_threshold = 0.5

    def process_input(self, data: Dict) -> Dict:
        """Process input data with enhanced pattern recognition and adaptive learning"""
        # Record initial state for adaptation
        initial_knowledge = self.growth_state.knowledge
        
        # Extract and learn from patterns
        patterns = self._extract_patterns(data)
        learning_result = self._learn_from_patterns(patterns)
        
        # Adapt traits based on learning effectiveness
        self._adapt_traits(initial_knowledge, learning_result['knowledge_gain'])
        
        # Update growth and share knowledge
        self._update_growth_state(learning_result)
        self._share_knowledge()
        
        # Track experience with metadata
        self.experiences.append({
            'input_type': next(iter(data.keys())),
            'patterns': patterns,
            'learning': learning_result,
            'energy_state': self.energy,
            'timestamp': time.time()
        })
        
        return {
            'processed': True,
            'patterns_found': len(patterns),
            'learning_gain': learning_result['knowledge_gain'],
            'current_energy': self.energy,
            'specialization': self.growth_state.specialization
        }

    def _extract_patterns(self, data: Dict) -> List[Dict]:
        """Enhanced pattern extraction with improved recognition capabilities"""
        patterns = []
        
        if 'text' in data:
            text_patterns = self._process_text(data['text'])
            patterns.extend(text_patterns)
            
        if 'numbers' in data:
            num_patterns = self._process_numbers(data['numbers'])
            patterns.extend(num_patterns)
            
        # New: Pattern correlation detection
        if len(patterns) > 1:
            correlation_pattern = self._detect_pattern_correlations(patterns)
            if correlation_pattern:
                patterns.append(correlation_pattern)
                
        return [p for p in patterns if p['significance'] > 0.3]

    def _process_text(self, text: str) -> List[Dict]:
        """Enhanced text processing with semantic analysis"""
        patterns = []
        
        # Basic frequency analysis
        vectorizer = CountVectorizer(stop_words='english', ngram_range=(1, 2))
        word_freq_matrix = vectorizer.fit_transform([text])
        
        # Advanced pattern detection using PCA
        if word_freq_matrix.shape[1] > 1:
            pca = PCA(n_components=min(word_freq_matrix.shape[1], 3))
            pca_result = pca.fit_transform(word_freq_matrix.toarray())
            
            for i, component in enumerate(pca_result.T):
                significance = np.abs(component).mean()
                if significance > 0.3:
                    patterns.append({
                        'type': 'text_semantic',
                        'component': i,
                        'significance': float(significance),
                        'features': vectorizer.get_feature_names_out().tolist()
                    })
        
        return patterns

    def _process_numbers(self, numbers: List[float]) -> List[Dict]:
        """Enhanced numerical pattern detection"""
        patterns = []
        
        if len(numbers) < 2:
            return patterns
            
        # Basic statistical patterns
        mean = float(np.mean(numbers))
        std = float(np.std(numbers))
        
        # Trend detection
        if len(numbers) > 2:
            trend = np.polyfit(range(len(numbers)), numbers, 1)[0]
            trend_significance = abs(trend) / (std if std > 0 else 1)
            
            if trend_significance > 0.3:
                patterns.append({
                    'type': 'numerical_trend',
                    'trend': float(trend),
                    'significance': float(trend_significance)
                })
        
        # Distribution pattern
        patterns.append({
            'type': 'numerical_distribution',
            'mean': mean,
            'std': std,
            'range': (float(min(numbers)), float(max(numbers))),
            'significance': float(1 / (1 + std))
        })
        
        return patterns

    def _detect_pattern_correlations(self, patterns: List[Dict]) -> Optional[Dict]:
        """Detect correlations between different patterns"""
        if len(patterns) < 2:
            return None
            
        significances = [p['significance'] for p in patterns]
        correlation = float(np.corrcoef(significances)[0, 1])
        
        if abs(correlation) > 0.7:
            return {
                'type': 'meta_pattern',
                'correlation': correlation,
                'significance': abs(correlation),
                'pattern_types': [p['type'] for p in patterns]
            }
        return None

    def _adapt_traits(self, initial_knowledge: float, knowledge_gain: float):
        """Adapt node traits based on learning effectiveness"""
        self.learning_history.append(knowledge_gain)
        
        if len(self.learning_history) >= 10:
            recent_effectiveness = np.mean(list(self.learning_history)[-10:])
            if recent_effectiveness < self.adaptation_threshold:
                # Increase learning rate if effectiveness is low
                self.traits.learning_rate *= 1.1
            else:
                # Gradually optimize energy efficiency
                self.traits.energy_efficiency *= 1.05

    def replicate(self) -> 'Node':
        """Enhanced replication with trait inheritance and mutation"""
        new_node = Node()
        
        # Inherit traits with controlled mutation
        for trait_name, value in vars(self.traits).items():
            mutation = np.random.normal(0, 0.05)  # Increased mutation rate
            setattr(new_node.traits, trait_name, max(0.01, value + mutation))
        
        # Inherit selective memory
        if self.long_term:
            top_memories = sorted(
                self.long_term.items(), 
                key=lambda x: x[1].get('impact', 0),
                reverse=True
            )[:3]
            
            for key, memory in top_memories:
                new_node.long_term[key] = memory.copy()
        
        return new_node

class Environment:
    def __init__(self):
        self.resources = 1000.0
        self.nodes: List[Node] = []
        self.time = 0
        self.event_history = deque(maxlen=1000)
        self.resource_history = deque(maxlen=1000)

    def simulate(self, steps: int = 1):
        """Run simulation for specified number of steps"""
        for _ in range(steps):
            self._simulate_step()
            self._record_state()
        
    def _simulate_step(self):
        """Single simulation step with enhanced logic"""
        for node in list(self.nodes):
            event = self.simulate_event()
            self.provide_resources(node, event)
            
            # Process input and check node state
            input_data = self.generate_input_data()
            result = node.process_input(input_data)
            
            # Handle node replication
            if self._should_replicate(node):
                self._handle_replication(node)
            
            # Remove dead nodes
            if node.energy <= 0:
                self.nodes.remove(node)
    
    def _should_replicate(self, node: Node) -> bool:
        """Determine if node should replicate based on multiple factors"""
        return (
            node.growth_state.maturity >= 0.8 and
            node.energy > 20.0 and
            len(self.nodes) < 100 and  # Prevent overpopulation
            self.resources > 100.0  # Ensure sufficient resources
        )
    
    def _handle_replication(self, node: Node):
        """Handle node replication process"""
        new_node = node.replicate()
        node.energy /= 2
        new_node.energy = node.energy
        
        # Add to environment
        self.add_node(new_node)
        
        # Create bidirectional connection
        node.connections.add(new_node)
        new_node.connections.add(node)
        
        # Limit connections to prevent network congestion
        if len(node.connections) > 5:
            oldest_connection = min(node.connections, key=lambda x: x.birth_time)
            node.connections.remove(oldest_connection)
            oldest_connection.connections.remove(node)

    def _record_state(self):
        """Record environment state for analysis"""
        self.resource_history.append(self.resources)
        average_energy = np.mean([node.energy for node in self.nodes]) if self.nodes else 0
        
        state = {
            'time': self.time,
            'resources': self.resources,
            'node_count': len(self.nodes),
            'average_energy': average_energy
        }
        self.event_history.append(state)

def visualize_network(environment: Environment):
    """Enhanced network visualization with node metrics"""
    G = nx.Graph()
    
    # Add nodes with metadata
    for node in environment.nodes:
        G.add_node(
            node.id,
            energy=node.energy,
            maturity=node.growth_state.maturity,
            knowledge=node.growth_state.knowledge,
            specialization=node.growth_state.specialization
        )
        
        # Add edges (connections)
        for connected_node in node.connections:
            G.add_edge(node.id, connected_node.id)
    
    # Calculate layout
    pos = nx.spring_layout(G)
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    
    # Draw nodes with size based on energy and color based on knowledge
    energies = [G.nodes[n]['energy'] for n in G.nodes()]
    knowledge = [G.nodes[n]['knowledge'] for n in G.nodes()]
    
    max_energy = max(energies) if energies else 1
    node_sizes = [max(100, e / max_energy * 500) for e in energies]
    
    nx.draw(
        G, pos,
        with_labels=True,
        node_size=node_sizes,
        node_color=knowledge,
        cmap=plt.cm.viridis,
        edge_color='gray',
        alpha=0.7
    )
    
    plt.title(f'AI Network Visualization\nNodes: {len(environment.nodes)} | Resources: {environment.resources:.1f}')
    plt.colorbar(label='Knowledge Level')
    
    return plt
