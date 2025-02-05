# Kaleidoscope AI: Script for Node Core Functionality
# File: /core/NodeCore.py

import uuid
import time
import numpy as np
from typing import Dict, Optional, List
from collections import deque
from dataclasses import dataclass

@dataclass
class GrowthState:
    maturity: float = 0.0
    knowledge: float = 0.0
    specialization: Optional[str] = None

@dataclass
class Traits:
    learning_rate: float = 0.1
    energy_efficiency: float = 1.0
    replication_threshold: float = 0.8

class Node:
    def __init__(self, node_id: Optional[str] = None):
        self.id = node_id or str(uuid.uuid4())
        self.creation_time = time.time()
        self.energy = 10.0
        self.growth_state = GrowthState()
        self.traits = Traits()

        # Memory Systems
        self.short_term_memory = deque(maxlen=100)
        self.long_term_memory: Dict[str, Dict] = {}
        self.connections = set()

    def process_input(self, data: Dict) -> Dict:
        """Process input data, updating knowledge and state."""
        knowledge_gain = self._analyze_data(data)
        self._update_growth(knowledge_gain)
        return {
            'knowledge_gain': knowledge_gain,
            'energy_remaining': self.energy,
            'maturity': self.growth_state.maturity
        }

    def replicate(self) -> Optional['Node']:
        """Replicates the node if conditions are met."""
        if self.energy > 5.0 and self.growth_state.maturity >= self.traits.replication_threshold:
            self.energy /= 2
            new_node = Node()
            new_node.traits = self._mutate_traits()
            self.connections.add(new_node.id)
            new_node.connections.add(self.id)
            return new_node
        return None

    def _analyze_data(self, data: Dict) -> float:
        """Analyze input data and calculate knowledge gain."""
        patterns_detected = self._extract_patterns(data)
        knowledge_gain = sum(pattern['impact'] for pattern in patterns_detected)
        energy_cost = knowledge_gain / self.traits.energy_efficiency
        if self.energy >= energy_cost:
            self.energy -= energy_cost
        else:
            knowledge_gain *= 0.5  # Penalty for insufficient energy
        return knowledge_gain

    def _extract_patterns(self, data: Dict) -> List[Dict]:
        """Extract meaningful patterns from data."""
        patterns = []
        for key, value in data.items():
            if isinstance(value, str):
                length = len(value)
                patterns.append({'type': 'text', 'impact': length * 0.01})
            elif isinstance(value, (int, float)):
                patterns.append({'type': 'numeric', 'impact': abs(value) * 0.01})
            elif isinstance(value, list) and all(isinstance(i, (int, float)) for i in value):
                mean_value = np.mean(value)
                patterns.append({'type': 'numeric_list', 'impact': mean_value * 0.01})
        return patterns

    def _update_growth(self, knowledge_gain: float):
        """Update growth state based on knowledge gain."""
        self.growth_state.knowledge += knowledge_gain
        self.growth_state.maturity = min(1.0, self.growth_state.maturity + knowledge_gain * self.traits.learning_rate)

    def _mutate_traits(self) -> Traits:
        """Mutate traits slightly during replication."""
        new_traits = Traits(
            learning_rate=max(0.01, self.traits.learning_rate + np.random.normal(0, 0.01)),
            energy_efficiency=max(0.5, self.traits.energy_efficiency + np.random.normal(0, 0.05)),
            replication_threshold=min(1.0, self.traits.replication_threshold + np.random.normal(0, 0.02))
        )
        return new_traits

    def communicate(self, target_node: 'Node', message: Dict):
        """Send a message to another node."""
        if target_node:
            if target_node.id in self.connections:
                target_node.receive_message({
                    'sender': self.id,
                    'timestamp': time.time(),
                    'content': message
                })
            else:
                raise ValueError(f"Target node {target_node.id} is not in the connections list.")

    def receive_message(self, message: Dict):
        """Receive and process a message."""
        self.short_term_memory.append(message)
        # Process the message (extend with specific logic as needed)

# Example Usage
if __name__ == "__main__":
    node1 = Node()
    node2 = Node()
    node1.connections.add(node2.id)
    node2.connections.add(node1.id)

    data = {"input1": "Example Data", "input2": "More Data", "numbers": [10, 20, 30]}
    result = node1.process_input(data)
    print(f"Node 1 Process Result: {result}")

    try:
        node1.communicate(node2, {"type": "greeting", "message": "Hello, Node 2!"})
        print("Message successfully sent to Node 2.")
    except ValueError as e:
        print(e)

    new_node = node1.replicate()
    if new_node:
        print(f"Node {new_node.id} replicated from Node {node1.id}")
