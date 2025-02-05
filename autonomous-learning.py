from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np
from collections import defaultdict

@dataclass
class LearningMetrics:
    """Tracks learning performance metrics."""
    pattern_accuracy: float = 0.0
    knowledge_coherence: float = 0.0
    insight_novelty: float = 0.0
    learning_rate: float = 0.1
    adaptation_score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class AutonomousLearning:
    """Manages the system's autonomous learning capabilities."""
    
    def __init__(self):
        self.pattern_weights = defaultdict(float)
        self.knowledge_connections = defaultdict(list)
        self.learning_history = []
        self.performance_metrics = []
        self.adaptation_threshold = 0.7
        
    def evaluate_performance(self, insights: List[Dict[str, Any]]) -> LearningMetrics:
        """Evaluates current system performance."""
        metrics = LearningMetrics()
        
        # Calculate pattern recognition accuracy
        metrics.pattern_accuracy = self._calculate_pattern_accuracy(insights)
        
        # Evaluate knowledge coherence
        metrics.knowledge_coherence = self._calculate_knowledge_coherence(insights)
        
        # Measure insight novelty
        metrics.insight_novelty = self._calculate_insight_novelty(insights)
        
        # Calculate adaptation score
        metrics.adaptation_score = self._calculate_adaptation_score(
            metrics.pattern_accuracy,
            metrics.knowledge_coherence,
            metrics.insight_novelty
        )
        
        self.performance_metrics.append(metrics)
        return metrics
        
    def adapt_parameters(self, metrics: LearningMetrics):
        """Adapts system parameters based on performance metrics."""
        if metrics.adaptation_score > self.adaptation_threshold:
            # Strengthen successful patterns
            self._strengthen_patterns()
            
            # Enhance knowledge connections
            self._enhance_connections()
            
            # Adjust learning rate
            self._adjust_learning_rate(metrics)
            
        self.learning_history.append({
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'adaptations_made': metrics.adaptation_score > self.adaptation_threshold
        })
        
    def _calculate_pattern_accuracy(self, insights: List[Dict[str, Any]]) -> float:
        """Calculates accuracy of pattern recognition."""
        if not insights:
            return 0.0
            
        accuracies = []
        for insight in insights:
            if 'pattern_matches' in insight:
                accuracy = insight.get('confidence', 0.0)
                accuracies.append(accuracy)
                
                # Update pattern weights
                for pattern in insight.get('patterns', []):
                    self.pattern_weights[pattern['id']] += accuracy
                    
        return np.mean(accuracies) if accuracies else 0.0
        
    def _calculate_knowledge_coherence(self, insights: List[Dict[str, Any]]) -> float:
        """Evaluates coherence of knowledge connections."""
        if not insights:
            return 0.0
            
        coherence_scores = []
        for insight in insights:
            connections = insight.get('connections', [])
            if connections:
                # Calculate connection strength
                strength = np.mean([conn.get('weight', 0.0) for conn in connections])
                coherence_scores.append(strength)
                
                # Store connections
                self.knowledge_connections[insight['id']].extend(connections)
                
        return np.mean(coherence_scores) if coherence_scores else 0.0
        
    def _calculate_insight_novelty(self, insights: List[Dict[str, Any]]) -> float:
        """Measures novelty of generated insights."""
        if not insights:
            return 0.0
            
        novelty_scores = []
        for insight in insights:
            # Check if insight connects previously unconnected patterns
            connections = insight.get('connections', [])
            existing_connections = set()
            for src_id in self.knowledge_connections:
                for conn in self.knowledge_connections[src_id]:
                    existing_connections.add(
                        (conn.get('source'), conn.get('target'))
                    )
                    
            new_connections = 0
            for conn in connections:
                pair = (conn.get('source'), conn.get('target'))
                if pair not in existing_connections:
                    new_connections += 1
                    
            if connections:
                novelty = new_connections / len(connections)
                novelty_scores.append(novelty)
                
        return np.mean(novelty_scores) if novelty_scores else 0.0
        
    def _calculate_adaptation_score(
        self,
        pattern_accuracy: float,
        knowledge_coherence: float,
        insight_novelty: float
    ) -> float:
        """Calculates overall adaptation score."""
        weights = {
            'pattern_accuracy': 0.4,
            'knowledge_coherence': 0.4,
            'insight_novelty': 0.2
        }
        
        return (
            weights['pattern_accuracy'] * pattern_accuracy +
            weights['knowledge_coherence'] * knowledge_coherence +
            weights['insight_novelty'] * insight_novelty
        )
        
    def _strengthen_patterns(self):
        """Strengthens successful pattern recognition."""
        if not self.pattern_weights:
            return
            
        # Normalize pattern weights
        total_weight = sum(self.pattern_weights.values())
        if total_weight > 0:
            for pattern_id in self.pattern_weights:
                self.pattern_weights[pattern_id] /= total_weight
                
    def _enhance_connections(self):
        """Enhances strong knowledge connections."""
        for insight_id in self.knowledge_connections:
            connections = self.knowledge_connections[insight_id]
            for conn in connections:
                # Strengthen high-weight connections
                if conn.get('weight', 0.0) > 0.7:
                    conn['weight'] = min(1.0, conn['weight'] * 1.1)
                    
    def _adjust_learning_rate(self, metrics: LearningMetrics):
        """Adjusts learning rate based on performance."""
        if metrics.adaptation_score > 0.8:
            # Reduce learning rate when performing well
            metrics.learning_rate *= 0.95
        elif metrics.adaptation_score < 0.5:
            # Increase learning rate when performance is poor
            metrics.learning_rate = min(1.0, metrics.learning_rate * 1.05)
            
    def get_learning_summary(self) -> Dict[str, Any]:
        """Generates summary of learning progress."""
        if not self.performance_metrics:
            return {}
            
        recent_metrics = self.performance_metrics[-10:]
        
        return {
            'total_iterations': len(self.performance_metrics),
            'current_performance': {
                'pattern_accuracy': self.performance_metrics[-1].pattern_accuracy,
                'knowledge_coherence': self.performance_metrics[-1].knowledge_coherence,
                'insight_novelty': self.performance_metrics[-1].insight_novelty
            },
            'learning_trends': {
                'pattern_accuracy': self._calculate_trend([m.pattern_accuracy for m in recent_metrics]),
                'knowledge_coherence': self._calculate_trend([m.knowledge_coherence for m in recent_metrics]),
                'insight_novelty': self._calculate_trend([m.insight_novelty for m in recent_metrics])
            },
            'adaptation_rate': np.mean([
                1 if entry['adaptations_made'] else 0
                for entry in self.learning_history[-10:]
            ])
        }
        
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculates trend in a series of values."""
        if len(values) < 2:
            return 0.0
        
        return (values[-1] - values[0]) / len(values)
