import wikipedia
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import uuid
import time
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from collections import deque
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import PCA

@dataclass
class GrowthState:
    maturity: float = 0.0
    knowledge: float = 0.0
    specialization: Optional[str] = None
    energy: float = 10.0

@dataclass
class Traits:
    learning_rate: float = 0.1
    adaptation_rate: float = 0.1
    energy_efficiency: float = 1.0
    pattern_recognition: float = 0.5

class WikiNode:
    def __init__(self, node_id: Optional[str] = None, parent_knowledge: Optional[Dict] = None):
        self.id = node_id or str(uuid.uuid4())
        self.birth_time = time.time()
        self.growth_state = GrowthState()
        self.traits = Traits()
        
        # Memory systems from original code
        self.short_term = deque(maxlen=100)
        self.long_term: Dict[str, Dict] = {}
        self.max_long_term = 1000
        
        # Wiki-specific memory
        self.knowledge_base = {}
        self.current_topic: Optional[str] = None
        self.explored_topics = set()
        
        # Growth tracking
        self.experiences = deque(maxlen=1000)
        self.growth_path = deque(maxlen=1000)
        self.connections = set()
        
        # Inherit from parent if provided
        if parent_knowledge:
            self._inherit_knowledge(parent_knowledge)

    def learn_from_wikipedia(self, starting_point: Optional[str] = None) -> Dict:
        """Learn from Wikipedia with energy management and pattern recognition"""
        try:
            # Energy cost for learning
            energy_cost = 1.0 / self.traits.energy_efficiency
            if self.growth_state.energy < energy_cost:
                return {"status": "low_energy", "next_topic": None}

            # Get page
            page_title = starting_point or wikipedia.random(1)
            wiki_page = wikipedia.page(page_title)
            
            # Extract patterns from content
            patterns = self._extract_patterns({
                'text': wiki_page.content[:5000],
                'title': wiki_page.title,
                'links': wiki_page.links
            })
            
            # Learn from patterns
            learning_result = self._learn_from_patterns(patterns)
            
            # Update growth state
            self._update_growth_state(learning_result)
            
            # Store knowledge
            self.knowledge_base[wiki_page.title] = {
                'content': wiki_page.content[:5000],
                'patterns': patterns,
                'links': wiki_page.links,
                'timestamp': time.time(),
                'energy_cost': energy_cost
            }
            
            # Update exploration status
            self.explored_topics.add(wiki_page.title)
            self.current_topic = wiki_page.title
            
            # Choose next topic based on patterns and energy
            next_topic = self._choose_next_topic(wiki_page.links, patterns)
            
            return {
                "status": "success",
                "next_topic": next_topic,
                "patterns_found": len(patterns),
                "energy_remaining": self.growth_state.energy
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e), "next_topic": None}

    def _extract_patterns(self, data: Dict) -> List[Dict]:
        """Enhanced pattern extraction from Wiki content"""
        patterns = []
        
        if 'text' in data:
            # Text pattern recognition from original code
            vectorizer = CountVectorizer(stop_words='english', ngram_range=(1, 2))
            text_matrix = vectorizer.fit_transform([data['text']])
            
            if text_matrix.shape[1] > 1:
                pca = PCA(n_components=min(text_matrix.shape[1], 3))
                pca_result = pca.fit_transform(text_matrix.toarray())
                
                for i, component in enumerate(pca_result.T):
                    significance = np.abs(component).mean()
                    if significance > 0.3:
                        patterns.append({
                            'type': 'semantic',
                            'component': i,
                            'significance': float(significance),
                            'features': vectorizer.get_feature_names_out().tolist()
                        })
        
        # Topic relationship patterns
        if 'links' in data:
            link_pattern = {
                'type': 'topic_network',
                'significance': len(data['links']) / 1000,
                'connected_topics': data['links'][:10]  # Top 10 related topics
            }
            patterns.append(link_pattern)
            
        return patterns

    def _learn_from_patterns(self, patterns: List[Dict]) -> Dict:
        """Learn from discovered patterns with energy consumption"""
        knowledge_gain = 0
        energy_spent = 0
        
        for pattern in patterns:
            impact = pattern['significance'] * self.traits.learning_rate
            energy_cost = impact / self.traits.energy_efficiency
            
            if self.growth_state.energy >= energy_cost:
                knowledge_gain += impact
                energy_spent += energy_cost
                self.growth_state.energy -= energy_cost
                
                # Store important patterns in long-term memory
                if pattern['significance'] > 0.5:
                    self.long_term[f"pattern_{len(self.long_term)}"] = {
                        'pattern': pattern,
                        'impact': impact,
                        'timestamp': time.time()
                    }
                else:
                    self.short_term.append({
                        'pattern': pattern,
                        'impact': impact,
                        'timestamp': time.time()
                    })
                    
        return {
            'knowledge_gain': knowledge_gain,
            'energy_spent': energy_spent,
            'patterns_processed': len(patterns)
        }

    def _update_growth_state(self, learning_result: Dict):
        """Update node's growth state based on learning"""
        self.growth_state.knowledge += learning_result['knowledge_gain']
        self.growth_state.maturity = min(1.0, 
            self.growth_state.maturity + 
            learning_result['knowledge_gain'] * self.traits.adaptation_rate
        )
        
        # Track growth
        self.growth_path.append({
            'knowledge': self.growth_state.knowledge,
            'maturity': self.growth_state.maturity,
            'energy': self.growth_state.energy,
            'timestamp': time.time()
        })

    def _choose_next_topic(self, available_links: List[str], patterns: List[Dict]) -> Optional[str]:
        """Choose next topic based on patterns and energy efficiency"""
        if not available_links or self.growth_state.energy < 5.0:
            return None
            
        # Find most promising topic based on patterns
        topic_scores = {}
        for link in available_links:
            if link not in self.explored_topics:
                # Score based on pattern relationships
                score = 0
                for pattern in patterns:
                    if pattern['type'] == 'semantic' and any(feature in link.lower() for feature in pattern['features']):
                        score += pattern['significance']
                    elif pattern['type'] == 'topic_network' and link in pattern['connected_topics']:
                        score += pattern['significance']
                
                topic_scores[link] = score
        
        if topic_scores:
            return max(topic_scores.items(), key=lambda x: x[1])[0]
        return random.choice(available_links)

    def replicate(self) -> 'WikiNode':
        """Create new node with inherited traits and knowledge"""
        new_node = WikiNode()
        
        # Inherit traits with mutation
        for trait_name, value in vars(self.traits).items():
            mutation = np.random.normal(0, 0.05)
            setattr(new_node.traits, trait_name, max(0.01, value + mutation))
        
        # Inherit key knowledge
        if self.long_term:
            top_memories = sorted(
                self.long_term.items(), 
                key=lambda x: x[1].get('impact', 0),
                reverse=True
            )[:3]
            for key, memory in top_memories:
                new_node.long_term[key] = memory.copy()
        
        return new_node

class WikiLearningNetwork:
    def __init__(self):
        self.nodes: Dict[str, WikiNode] = {}
        self.resources = 1000.0
        self.time = 0
        self.graph = nx.Graph()

    def simulate(self, steps: int):
        """Run network simulation"""
        if not self.nodes:
            self._initialize_network()
            
        for _ in range(steps):
            self._simulation_step()
            self._visualize_network()
            
    def _initialize_network(self):
        """Create initial node"""
        root_node = WikiNode("root")
        self.nodes["root"] = root_node
        self.graph.add_node("root")

    def _simulation_step(self):
        """Single simulation step"""
        for node_id, node in list(self.nodes.items()):
            # Provide resources
            self._provide_resources(node)
            
            # Let node learn
            result = node.learn_from_wikipedia()
            
            # Handle replication
            if self._should_replicate(node):
                self._handle_replication(node)
            
            # Remove dead nodes
            if node.growth_state.energy <= 0:
                self.nodes.pop(node_id)
                self.graph.remove_node(node_id)

    def _should_replicate(self, node: WikiNode) -> bool:
        """Determine if node should replicate"""
        return (
            node.growth_state.maturity >= 0.8 and
            node.growth_state.energy > 20.0 and
            len(self.nodes) < 100 and
            self.resources > 100.0
        )

    def _handle_replication(self, parent_node: WikiNode):
        """Handle node replication"""
        new_node = parent_node.replicate()
        self.nodes[new_node.id] = new_node
        
        # Update network
        self.graph.add_node(new_node.id)
        self.graph.add_edge(parent_node.id, new_node.id)
        
        # Split energy
        parent_node.growth_state.energy /= 2
        new_node.growth_state.energy = parent_node.growth_state.energy

    def _provide_resources(self, node: WikiNode):
        """Provide resources to node"""
        if self.resources > 0:
            resource_amount = 5.0
            self.resources -= resource_amount
            node.growth_state.energy += resource_amount * node.traits.energy_efficiency
        else:
            node.growth_state.energy -= 0.1

    def _visualize_network(self):
        """Visualize network state"""
        plt.clf()
        pos = nx.spring_layout(self.graph)
        
        # Node colors based on knowledge level
        colors = [self.nodes[n].growth_state.knowledge for n in self.graph.nodes()]
        sizes = [self.nodes[n].growth_state.energy * 10 for n in self.graph.nodes()]
        
        nx.draw(self.graph, pos,
               node_color=colors,
               node_size=sizes,
               with_labels=True,
               cmap=plt.cm.viridis)
        
        plt.title(f"Wiki Learning Network\nNodes: {len(self.nodes)} | Resources: {self.resources:.1f}")
        plt.pause(0.1)

# Example usage
network = WikiLearningNetwork()
network.simulate(steps=20)
