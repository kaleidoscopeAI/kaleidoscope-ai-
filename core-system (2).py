import numpy as np
import threading
import queue
from typing import Dict, List, Optional
from pathlib import Path
import logging
from dataclasses import dataclass, field
import networkx as nx
from collections import defaultdict

@dataclass 
class Node:
    """Represents a processing node in the system"""
    node_id: int
    memory_threshold: float
    memory_used: float = 0.0
    dna: Dict = field(default_factory=lambda: {
        "data_characteristics": [],
        "embedded_insights": [],
        "perspectives": []
    })
    data_buffer: List = field(default_factory=list)
    
    def ingest_data(self, data_chunk: Dict) -> Optional[Dict]:
        """Ingest data chunk and return processed insights if threshold met"""
        chunk_size = float(len(str(data_chunk)))
        if self.memory_used + chunk_size > self.memory_threshold:
            return None
            
        self.data_buffer.append(data_chunk)
        self.memory_used += chunk_size
        
        # Extract and embed characteristics
        self.dna["data_characteristics"].extend(
            self._extract_characteristics(data_chunk)
        )
        
        # Return processed insights if threshold met
        if self.memory_used >= self.memory_threshold:
            return self._process_buffer()
        return None
        
    def _extract_characteristics(self, data: Dict) -> List[Dict]:
        """Extract key characteristics from data"""
        characteristics = []
        try:
            # Statistical characteristics
            if isinstance(data.get("values"), (list, np.ndarray)):
                values = np.array(data["values"])
                characteristics.append({
                    "type": "statistical",
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "skew": float(self._calculate_skew(values))
                })
            
            # Structural characteristics
            if isinstance(data.get("structure"), dict):
                characteristics.append({
                    "type": "structural",
                    "depth": self._calculate_depth(data["structure"]),
                    "branching_factor": self._calculate_branching(data["structure"]),
                    "density": self._calculate_density(data["structure"])
                })
                
            # Temporal characteristics
            if "timestamp" in data:
                characteristics.append({
                    "type": "temporal",
                    "period": self._estimate_period(data),
                    "trend": self._estimate_trend(data),
                    "seasonality": self._check_seasonality(data)
                })
                
        except Exception as e:
            logging.error(f"Error extracting characteristics: {e}")
            
        return characteristics

    def _process_buffer(self) -> Dict:
        """Process buffered data into light insights"""
        insights = {
            "source_node": self.node_id,
            "data_volume": self.memory_used,
            "patterns": self._find_patterns(),
            "correlations": self._find_correlations(),
            "anomalies": self._detect_anomalies(),
            "embedded_dna": self.dna.copy()
        }
        
        # Clear buffer
        self.data_buffer = []
        self.memory_used = 0
        
        return insights
        
    def _calculate_skew(self, values: np.ndarray) -> float:
        """Calculate distribution skewness"""
        n = len(values)
        if n < 2:
            return 0.0
        delta = values - np.mean(values)
        skew = np.sum(delta**3) / ((n-1) * np.std(values)**3)
        return skew

    def _calculate_depth(self, structure: Dict, current_depth: int = 0) -> int:
        """Calculate maximum depth of nested structure"""
        if not isinstance(structure, dict):
            return current_depth
        depths = [
            self._calculate_depth(v, current_depth + 1)
            for v in structure.values()
            if isinstance(v, dict)
        ]
        return max(depths) if depths else current_depth + 1

    def _calculate_branching(self, structure: Dict) -> float:
        """Calculate average branching factor"""
        branches = []
        queue = [structure]
        while queue:
            current = queue.pop(0)
            if isinstance(current, dict):
                children = [v for v in current.values() if isinstance(v, dict)]
                branches.append(len(children))
                queue.extend(children)
        return np.mean(branches) if branches else 0

    def _calculate_density(self, structure: Dict) -> float:
        """Calculate structural density"""
        total_elements = 0
        max_possible = 0
        queue = [structure]
        while queue:
            current = queue.pop(0)
            if isinstance(current, dict):
                n_children = len(current)
                total_elements += n_children
                max_possible += n_children * 2
                queue.extend(v for v in current.values() if isinstance(v, dict))
        return total_elements / max_possible if max_possible > 0 else 0

    def _find_patterns(self) -> List[Dict]:
        """Find patterns in buffered data"""
        patterns = []
        try:
            # Create graph representation
            graph = nx.Graph()
            for chunk in self.data_buffer:
                if isinstance(chunk.get("structure"), dict):
                    self._add_structure_to_graph(graph, chunk["structure"])
            
            # Find common subgraphs
            if len(graph) > 0:
                subgraphs = self._find_frequent_subgraphs(graph)
                patterns.extend([
                    {
                        "type": "structural",
                        "pattern": self._subgraph_to_dict(sg),
                        "frequency": freq
                    }
                    for sg, freq in subgraphs
                ])
                
            # Find sequence patterns
            if any("sequence" in chunk for chunk in self.data_buffer):
                sequences = [
                    chunk["sequence"] 
                    for chunk in self.data_buffer 
                    if "sequence" in chunk
                ]
                seq_patterns = self._find_sequence_patterns(sequences)
                patterns.extend(seq_patterns)
                
        except Exception as e:
            logging.error(f"Error finding patterns: {e}")
            
        return patterns

    def _find_correlations(self) -> List[Dict]:
        """Find correlations in buffered data"""
        correlations = []
        try:
            # Extract numerical series
            series = defaultdict(list)
            for chunk in self.data_buffer:
                if isinstance(chunk.get("values"), (list, np.ndarray)):
                    for i, v in enumerate(chunk["values"]):
                        series[f"series_{i}"].append(v)
                        
            # Calculate correlations
            for name1, s1 in series.items():
                for name2, s2 in series.items():
                    if name1 < name2:  # Avoid duplicate pairs
                        if len(s1) == len(s2):
                            corr = np.corrcoef(s1, s2)[0,1]
                            if abs(corr) > 0.7:  # Strong correlation threshold
                                correlations.append({
                                    "series1": name1,
                                    "series2": name2,
                                    "correlation": float(corr)
                                })
                                
        except Exception as e:
            logging.error(f"Error finding correlations: {e}")
            
        return correlations

    def _detect_anomalies(self) -> List[Dict]:
        """Detect anomalies in buffered data"""
        anomalies = []
        try:
            for chunk in self.data_buffer:
                if isinstance(chunk.get("values"), (list, np.ndarray)):
                    values = np.array(chunk["values"])
                    mean = np.mean(values)
                    std = np.std(values)
                    threshold = 3 * std  # 3-sigma rule
                    
                    anomaly_indices = np.where(abs(values - mean) > threshold)[0]
                    for idx in anomaly_indices:
                        anomalies.append({
                            "type": "value",
                            "index": int(idx),
                            "value": float(values[idx]),
                            "deviation": float(abs(values[idx] - mean) / std)
                        })
                        
            # Structural anomalies
            if len(self.dna["data_characteristics"]) > 0:
                expected_structure = self._get_expected_structure()
                for chunk in self.data_buffer:
                    if isinstance(chunk.get("structure"), dict):
                        diff = self._compare_structures(
                            expected_structure,
                            chunk["structure"]
                        )
                        if diff > 0.5:  # High structural difference
                            anomalies.append({
                                "type": "structural",
                                "difference": float(diff)
                            })
                            
        except Exception as e:
            logging.error(f"Error detecting anomalies: {e}")
            
        return anomalies

    def _get_expected_structure(self) -> Dict:
        """Get expected data structure from DNA"""
        struct_chars = [
            c for c in self.dna["data_characteristics"]
            if c["type"] == "structural"
        ]
        if not struct_chars:
            return {}
            
        # Average structural characteristics
        avg_depth = np.mean([c["depth"] for c in struct_chars])
        avg_branching = np.mean([c["branching_factor"] for c in struct_chars])
        
        # Generate expected structure
        return self._generate_structure(int(avg_depth), avg_branching)

    def _generate_structure(self, depth: int, branching: float) -> Dict:
        """Generate structure with given characteristics"""
        if depth <= 0:
            return {}
            
        n_children = int(round(branching))
        return {
            f"node_{i}": self._generate_structure(depth - 1, branching)
            for i in range(n_children)
        }

class Membrane:
    """Manages data distribution and node orchestration"""
    def __init__(self, total_data_size: float):
        self.total_data_size = total_data_size
        self.nodes: List[Node] = []
        self.environment = []
        self.node_id_counter = 0
        
    def calculate_resources(self, target_insights: int) -> Dict:
        """Calculate required number of nodes and memory per node"""
        # Theoretical relationship between data, nodes and insights
        # insights = k * (nodes * memory)^0.7
        # where k is efficiency factor
        k = 0.1  # Efficiency factor
        
        # Solve for n_nodes * memory = x
        x = (target_insights / k) ** (1/0.7)
        
        # Optimize node count vs memory per node
        # More nodes = more parallel processing but higher overhead
        # More memory per node = better pattern recognition but slower processing
        
        n_nodes = int(np.sqrt(x))  # Balance between nodes and memory
        memory_per_node = x / n_nodes
        
        return {
            "n_nodes": n_nodes,
            "memory_per_node": memory_per_node
        }
        
    def populate_nodes(self, n_nodes: int, memory_per_node: float):
        """Create and initialize nodes"""
        for _ in range(n_nodes):
            node = Node(
                node_id=self.node_id_counter,
                memory_threshold=memory_per_node
            )
            self.nodes.append(node)
            self.node_id_counter += 1
            
    def distribute_data(self, data_chunks: List[Dict]):
        """Distribute data chunks to nodes"""
        node_idx = 0
        for chunk in data_chunks:
            # Round-robin distribution
            while True:
                node = self.nodes[node_idx]
                result = node.ingest_data(chunk)
                
                if result is not None:
                    # Node reached threshold, add insights to environment
                    self.environment.append(result)
                    
                if node.memory_used < node.memory_threshold:
                    break
                    
                node_idx = (node_idx + 1) % len(self.nodes)
