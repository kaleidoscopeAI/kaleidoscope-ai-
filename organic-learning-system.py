import numpy as np
import networkx as nx
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, Counter
import wikipedia
import time
import uuid
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cosine

@dataclass
class GeneticCode:
    """Base 'DNA' that defines node behavior and growth patterns"""
    validation_threshold: float = 0.7
    learning_rate: float = 0.1
    mutation_rate: float = 0.01
    energy_efficiency: float = 1.0
    memory_capacity: int = 1000
    specialization_tendency: float = 0.5
    connection_strength: float = 0.3
    truth_sensitivity: float = 0.8

@dataclass
class Knowledge:
    """Individual unit of knowledge with truth validation"""
    content: str
    source: str
    timestamp: float
    truth_score: float = 0.5  # Initial neutral score
    validation_count: int = 1
    contradictions: List[str] = None
    supporting_facts: List[str] = None
    related_topics: Set[str] = None
    
    def __post_init__(self):
        self.contradictions = self.contradictions or []
        self.supporting_facts = self.supporting_facts or []
        self.related_topics = self.related_topics or set()

class OrganicNode:
    def __init__(self, genetic_code: Optional[GeneticCode] = None):
        self.id = str(uuid.uuid4())
        self.dna = genetic_code or GeneticCode()
        self.birth_time = time.time()
        
        # Knowledge structure like cell nucleus
        self.knowledge_base: Dict[str, Knowledge] = {}
        self.truth_matrix: Dict[str, float] = defaultdict(float)
        self.contradiction_map: Dict[str, Set[str]] = defaultdict(set)
        
        # Cell-like components
        self.energy = 10.0
        self.maturity = 0.0
        self.specialization = None
        self.connections = set()
        
        # Memory organization (like organelles)
        self.short_term_memory = []
        self.long_term_memory: Dict[str, Knowledge] = {}
        self.validation_queue = []

    def process_information(self, content: str, source: str) -> Dict:
        """Process new information like cellular protein synthesis"""
        # Energy check
        if self.energy < 1.0:
            return {"status": "insufficient_energy"}
            
        try:
            # Extract key facts and compute initial truth score
            facts = self._extract_facts(content)
            initial_score = self._compute_initial_truth_score(facts)
            
            # Create knowledge unit
            knowledge = Knowledge(
                content=content,
                source=source,
                timestamp=time.time(),
                truth_score=initial_score
            )
            
            # Validate against existing knowledge
            validation_result = self._validate_knowledge(knowledge, facts)
            
            # Update truth scores based on validation
            self._update_truth_scores(validation_result)
            
            # Store validated knowledge
            if validation_result['truth_score'] > self.dna.validation_threshold:
                self._store_knowledge(knowledge, validation_result)
            
            return {
                "status": "success",
                "truth_score": validation_result['truth_score'],
                "contradictions": validation_result['contradictions'],
                "supporting_evidence": validation_result['supporting']
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _extract_facts(self, content: str) -> List[str]:
        """Extract individual facts from content (like RNA transcription)"""
        # Use TF-IDF to identify key statements
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([content])
        
        # Extract sentences with highest TF-IDF scores
        sentences = content.split('.')
        sentence_scores = []
        
        for sentence in sentences:
            if len(sentence.strip()) > 0:
                sentence_vector = vectorizer.transform([sentence])
                score = np.mean(sentence_vector.toarray())
                sentence_scores.append((sentence.strip(), score))
        
        # Return top scoring sentences as facts
        return [s[0] for s in sorted(sentence_scores, key=lambda x: x[1], reverse=True)[:5]]

    def _compute_initial_truth_score(self, facts: List[str]) -> float:
        """Compute initial truth score based on existing knowledge"""
        if not self.knowledge_base:
            return 0.5  # Neutral score for first fact
            
        scores = []
        for fact in facts:
            # Compare with existing knowledge
            for known_fact in self.knowledge_base.values():
                similarity = self._compute_similarity(fact, known_fact.content)
                if similarity > 0.7:  # High similarity threshold
                    scores.append(known_fact.truth_score)
                    
        return np.mean(scores) if scores else 0.5

    def _validate_knowledge(self, knowledge: Knowledge, facts: List[str]) -> Dict:
        """Validate new knowledge against existing knowledge (like immune system)"""
        contradictions = []
        supporting = []
        
        for fact in facts:
            for existing_knowledge in self.knowledge_base.values():
                similarity = self._compute_similarity(fact, existing_knowledge.content)
                
                if similarity > 0.7:
                    # Check for contradiction
                    if abs(existing_knowledge.truth_score - knowledge.truth_score) > 0.5:
                        contradictions.append({
                            'fact': fact,
                            'existing': existing_knowledge.content,
                            'truth_score': existing_knowledge.truth_score
                        })
                    else:
                        supporting.append({
                            'fact': fact,
                            'existing': existing_knowledge.content,
                            'truth_score': existing_knowledge.truth_score
                        })
        
        # Compute final truth score
        final_score = self._compute_consensus_truth_score(knowledge.truth_score, 
                                                        contradictions, 
                                                        supporting)
        
        return {
            'truth_score': final_score,
            'contradictions': contradictions,
            'supporting': supporting
        }

    def _compute_consensus_truth_score(self, 
                                     initial_score: float, 
                                     contradictions: List[Dict], 
                                     supporting: List[Dict]) -> float:
        """Compute consensus truth score (like cellular decision making)"""
        if not contradictions and not supporting:
            return initial_score
            
        # Weight evidence based on quantity and quality
        contradiction_weight = sum(c['truth_score'] for c in contradictions)
        supporting_weight = sum(s['truth_score'] for s in supporting)
        
        # Apply DNA sensitivity parameter
        weighted_score = (
            initial_score + 
            (supporting_weight - contradiction_weight) * self.dna.truth_sensitivity
        ) / (1 + len(contradictions) + len(supporting))
        
        return max(0.0, min(1.0, weighted_score))

    def _compute_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between texts"""
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf = vectorizer.fit_transform([text1, text2])
            return 1 - cosine(tfidf.toarray()[0], tfidf.toarray()[1])
        except:
            return 0.0

    def _store_knowledge(self, knowledge: Knowledge, validation_result: Dict):
        """Store validated knowledge (like cellular memory)"""
        # Update contradiction map
        for contradiction in validation_result['contradictions']:
            self.contradiction_map[knowledge.content].add(contradiction['fact'])
            
        # Update truth matrix
        self.truth_matrix[knowledge.content] = validation_result['truth_score']
        
        # Store in appropriate memory system
        if validation_result['truth_score'] > 0.8:
            self.long_term_memory[knowledge.content] = knowledge
        else:
            self.short_term_memory.append(knowledge)
            
        # Maintain memory limits
        while len(self.short_term_memory) > self.dna.memory_capacity:
            self.short_term_memory.pop(0)

    def replicate(self) -> 'OrganicNode':
        """Create new node with inherited DNA (like cell division)"""
        # Create mutated DNA
        new_dna = GeneticCode()
        for attr in vars(self.dna):
            original_value = getattr(self.dna, attr)
            mutation = np.random.normal(0, self.dna.mutation_rate)
            new_value = max(0.01, original_value + mutation)
            setattr(new_dna, attr, new_value)
            
        # Create new node
        child = OrganicNode(new_dna)
        
        # Inherit most reliable knowledge
        reliable_knowledge = {
            k: v for k, v in self.long_term_memory.items() 
            if v.truth_score > 0.9
        }
        
        top_knowledge = dict(sorted(
            reliable_knowledge.items(), 
            key=lambda x: x[1].truth_score,
            reverse=True
        )[:10])
        
        child.long_term_memory.update(top_knowledge)
        
        return child

class OrganicNetwork:
    def __init__(self):
        self.nodes: Dict[str, OrganicNode] = {}
        self.graph = nx.Graph()
        self.resources = 1000.0

    def grow(self, steps: int):
        """Grow network organically"""
        if not self.nodes:
            self._plant_seed()
            
        for _ in range(steps):
            self._growth_cycle()
            self._visualize()

    def _plant_seed(self):
        """Create initial seed node with base knowledge"""
        seed = OrganicNode()
        self.nodes[seed.id] = seed
        self.graph.add_node(seed.id)
        
        # Process some initial Wikipedia content
        try:
            page = wikipedia.page("Scientific method")
            seed.process_information(page.content[:5000], "wikipedia")
        except:
            pass

    def _growth_cycle(self):
        """Single growth cycle"""
        for node_id, node in list(self.nodes.items()):
            # Provide resources
            if self.resources > 0:
                resource_amount = 5.0
                self.resources -= resource_amount
                node.energy += resource_amount * node.dna.energy_efficiency
            
            # Process new information
            try:
                page = wikipedia.random(1)
                wiki_page = wikipedia.page(page)
                node.process_information(wiki_page.content[:5000], "wikipedia")
            except:
                continue
                
            # Check replication conditions
            if (node.energy > 20.0 and 
                len(node.long_term_memory) > 50 and 
                len(self.nodes) < 100):
                self._handle_replication(node)
                
            # Remove dead nodes
            if node.energy <= 0:
                self.nodes.pop(node_id)
                self.graph.remove_node(node_id)

    def _handle_replication(self, parent: OrganicNode):
        """Handle node replication"""
        child = parent.replicate()
        self.nodes[child.id] = child
        
        # Update network
        self.graph.add_node(child.id)
        self.graph.add_edge(parent.id, child.id)
        
        # Split energy
        parent.energy /= 2
        child.energy = parent.energy

    def _visualize(self):
        """Visualize network state"""
        plt.clf()
        pos = nx.spring_layout(self.graph)
        
        # Node colors based on knowledge validation scores
        colors = [
            np.mean([k.truth_score for k in self.nodes[n].long_term_memory.values()])
            if self.nodes[n].long_term_memory else 0
            for n in self.graph.nodes()
        ]
        
        sizes = [len(self.nodes[n].long_term_memory) * 10 for n in self.graph.nodes()]
        
        nx.draw(self.graph, pos,
               node_color=colors,
               node_size=sizes,
               with_labels=True,
               cmap=plt.cm.RdYlGn)  # Red to Green color map for truth scores
        
        plt.title(f"Organic Learning Network\nNodes: {len(self.nodes)} | Resources: {self.resources:.1f}")
        plt.pause(0.1)

# Example usage
network = OrganicNetwork()
network.grow(steps=20)
