class DualEngineSystem:
    def __init__(self):
        self.kaleidoscope = Engine(is_ethical=True)
        self.mirrored = Engine(is_ethical=False)
        self.clusters = []

    def process_data(self, raw_data):
        # Process through both engines
        k_insights = self.kaleidoscope.process_data(raw_data)
        m_insights = self.mirrored.process_data(raw_data)
        
        # Create representative nodes
        k_node = self.kaleidoscope.crystallize([], k_insights)
        m_node = self.mirrored.crystallize([], m_insights)
        
        return k_node, m_node

    def create_cluster(self, nodes):
        """Create cluster from representative nodes."""
        cluster = {
            'ethical': [n[0] for n in nodes],
            'unbound': [n[1] for n in nodes]
        }
        self.clusters.append(cluster)
        return cluster

    def simulate_interaction(self, cluster1, cluster2):
        """Simulate interaction between clusters."""
        results = {
            'ethical': self._interact(cluster1['ethical'], cluster2['ethical']),
            'unbound': self._interact(cluster1['unbound'], cluster2['unbound'])
        }
        return results

    def _interact(self, nodes1, nodes2):
        """Core interaction logic between node sets."""
        interactions = []
        for n1 in nodes1:
            for n2 in nodes2:
                # Compare memory patterns
                pattern_match = len(
                    set(str(m) for m in n1.memory) &
                    set(str(m) for m in n2.memory)
                )
                interactions.append({
                    'strength': pattern_match,
                    'patterns': pattern_match / max(len(n1.memory), len(n2.memory))
                })
        return interactions

# Example usage for cancer cell analysis
if __name__ == "__main__":
    # Initialize system
    system = DualEngineSystem()
    
    # Process cancer cell data
    cancer_data = {
        'type': 'cell',
        'growth_rate': 0.75,
        'risk': 0.9,
        'markers': ['m1', 'm2']
    }
    
    k_node, m_node = system.process_data(cancer_data)
    cluster1 = system.create_cluster([(k_node, m_node)])
    
    # Process compound data
    compound_data = {
        'type': 'compound',
        'reactivity': 0.8,
        'toxicity': 0.3,
        'targets': ['m1']
    }
    
    k_node2, m_node2 = system.process_data(compound_data)
    cluster2 = system.create_cluster([(k_node2, m_node2)])
    
    # Simulate interaction
    results = system.simulate_interaction(cluster1, cluster2)
    print("Interaction Results:", results)
