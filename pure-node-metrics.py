from __future__ import annotations
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
from collections import deque

logger = logging.getLogger(__name__)

@dataclass
class InteractionMetric:
    """Tracks metrics for node interactions."""
    timestamp: datetime
    interaction_type: str
    success: bool
    energy_change: float
    duration: float
    participants: List[str]
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReactionMetric:
    """Tracks metrics for chemical reactions."""
    timestamp: datetime
    reaction_type: str
    reactants: List[str]
    products: List[str]
    energy_delta: float
    yield_rate: float
    catalyst_effect: Optional[float] = None
    side_products: List[str] = field(default_factory=list)

@dataclass
class StructuralMetric:
    """Tracks structural changes in the node."""
    timestamp: datetime
    change_type: str
    previous_state: Dict[str, Any]
    new_state: Dict[str, Any]
    stability_impact: float
    energy_cost: float

class PureNodeMetrics:
    """
    Comprehensive metrics tracking system for pure nodes.
    Monitors interactions, reactions, structural changes, and performance.
    """

    def __init__(self, max_history: int = 1000):
        # General metrics
        self.creation_time = datetime.now()
        self.total_interactions = 0
        self.successful_interactions = 0
        self.total_reactions = 0
        self.total_energy_changes = 0.0
        
        # Detailed metrics storage
        self.interaction_history = deque(maxlen=max_history)
        self.reaction_history = deque(maxlen=max_history)
        self.structural_history = deque(maxlen=max_history)
        
        # Performance metrics
        self.processing_times = deque(maxlen=100)
        self.energy_efficiency = deque(maxlen=100)
        self.stability_scores = deque(maxlen=100)
        
        # Statistical aggregates
        self.running_stats = {
            "avg_interaction_success_rate": 0.0,
            "avg_reaction_yield": 0.0,
            "avg_energy_efficiency": 0.0,
            "avg_structural_stability": 1.0
        }
        
        logger.info("PureNodeMetrics initialized")

    def record_interaction(self, interaction_data: Dict[str, Any]):
        """Records metrics for an interaction event."""
        try:
            metric = InteractionMetric(
                timestamp=datetime.now(),
                interaction_type=interaction_data.get("type", "unknown"),
                success=interaction_data.get("success", False),
                energy_change=interaction_data.get("energy_change", 0.0),
                duration=interaction_data.get("duration", 0.0),
                participants=interaction_data.get("participants", []),
                details=interaction_data.get("details", {})
            )
            
            self.interaction_history.append(metric)
            self.total_interactions += 1
            if metric.success:
                self.successful_interactions += 1
            self.total_energy_changes += metric.energy_change
            
            # Update running statistics
            self._update_interaction_stats(metric)
            
            logger.debug(f"Recorded interaction metric: {metric}")
            
        except Exception as e:
            logger.error(f"Error recording interaction metric: {str(e)}")

    def record_reaction(self, reaction_data: Dict[str, Any]):
        """Records metrics for a chemical reaction."""
        try:
            metric = ReactionMetric(
                timestamp=datetime.now(),
                reaction_type=reaction_data.get("type", "unknown"),
                reactants=reaction_data.get("reactants", []),
                products=reaction_data.get("products", []),
                energy_delta=reaction_data.get("energy_delta", 0.0),
                yield_rate=reaction_data.get("yield_rate", 0.0),
                catalyst_effect=reaction_data.get("catalyst_effect"),
                side_products=reaction_data.get("side_products", [])
            )
            
            self.reaction_history.append(metric)
            self.total_reactions += 1
            
            # Update running statistics
            self._update_reaction_stats(metric)
            
            logger.debug(f"Recorded reaction metric: {metric}")
            
        except Exception as e:
            logger.error(f"Error recording reaction metric: {str(e)}")

    def record_structural_change(self, change_data: Dict[str, Any]):
        """Records metrics for structural changes."""
        try:
            metric = StructuralMetric(
                timestamp=datetime.now(),
                change_type=change_data.get("type", "unknown"),
                previous_state=change_data.get("previous_state", {}),
                new_state=change_data.get("new_state", {}),
                stability_impact=change_data.get("stability_impact", 0.0),
                energy_cost=change_data.get("energy_cost", 0.0)
            )
            
            self.structural_history.append(metric)
            
            # Update stability scores
            self.stability_scores.append(metric.stability_impact)
            
            # Update running statistics
            self._update_structural_stats(metric)
            
            logger.debug(f"Recorded structural metric: {metric}")
            
        except Exception as e:
            logger.error(f"Error recording structural metric: {str(e)}")

    def record_performance(self, processing_time: float, energy_used: float):
        """Records performance metrics."""
        self.processing_times.append(processing_time)
        self.energy_efficiency.append(energy_used)
        
        # Update running statistics
        self._update_performance_stats(processing_time, energy_used)

    def _update_interaction_stats(self, metric: InteractionMetric):
        """Updates running statistics for interactions."""
        if self.total_interactions > 0:
            self.running_stats["avg_interaction_success_rate"] = (
                self.successful_interactions / self.total_interactions
            )
        
        # Calculate moving averages for energy efficiency
        if self.energy_efficiency:
            self.running_stats["avg_energy_efficiency"] = np.mean(self.energy_efficiency)

    def _update_reaction_stats(self, metric: ReactionMetric):
        """Updates running statistics for reactions."""
        # Update average reaction yield
        yields = [m.yield_rate for m in self.reaction_history if m.yield_rate is not None]
        if yields:
            self.running_stats["avg_reaction_yield"] = np.mean(yields)

    def _update_structural_stats(self, metric: StructuralMetric):
        """Updates running statistics for structural changes."""
        if self.stability_scores:
            self.running_stats["avg_structural_stability"] = np.mean(self.stability_scores)

    def _update_performance_stats(self, processing_time: float, energy_used: float):
        """Updates running statistics for performance metrics."""
        if self.processing_times:
            avg_processing_time = np.mean(self.processing_times)
            avg_energy_efficiency = np.mean(self.energy_efficiency)
            
            # Update energy efficiency metric
            self.running_stats["avg_energy_efficiency"] = (
                avg_energy_efficiency / avg_processing_time
                if avg_processing_time > 0 else 0.0
            )

    def get_summary(self) -> Dict[str, Any]:
        """Returns a summary of all metrics."""
        return {
            "general": {
                "uptime": (datetime.now() - self.creation_time).total_seconds(),
                "total_interactions": self.total_interactions,
                "successful_interactions": self.successful_interactions,
                "total_reactions": self.total_reactions,
                "total_energy_changes": self.total_energy_changes
            },
            "performance": {
                "avg_processing_time": np.mean(self.processing_times) if self.processing_times else 0.0,
                "avg_energy_efficiency": self.running_stats["avg_energy_efficiency"],
                "avg_stability": self.running_stats["avg_structural_stability"]
            },
            "interactions": {
                "success_rate": self.running_stats["avg_interaction_success_rate"],
                "recent_interactions": len(self.interaction_history)
            },
            "reactions": {
                "avg_yield": self.running_stats["avg_reaction_yield"],
                "recent_reactions": len(self.reaction_history)
            }
        }

    def export_metrics(self, format: str = "json") -> str:
        """Exports metrics in specified format."""
        metrics = self.get_summary()
        
        if format.lower() == "json":
            return json.dumps(metrics, indent=2)
        elif format.lower() == "csv":
            # Convert to CSV format
            csv_lines = ["metric,value"]
            for category, values in metrics.items():
                for key, value in values.items():
                    csv_lines.append(f"{category}.{key},{value}")
            return "\n".join(csv_lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def analyze_trends(self) -> Dict[str, Any]:
        """Analyzes trends in metrics over time."""
        return {
            "interaction_success_trend": self._calculate_trend(
                [m.success for m in self.interaction_history]
            ),
            "energy_efficiency_trend": self._calculate_trend(self.energy_efficiency),
            "stability_trend": self._calculate_trend(self.stability_scores),
            "reaction_yield_trend": self._calculate_trend(
                [m.yield_rate for m in self.reaction_history]
            )
        }

    def _calculate_trend(self, values: List[float], window_size: int = 10) -> Dict[str, float]:
        """Calculates trend metrics for a series of values."""
        if not values:
            return {"slope": 0.0, "variance": 0.0}
            
        values = list(values)  # Convert deque to list if necessary
        if len(values) < 2:
            return {"slope": 0.0, "variance": 0.0}
            
        # Calculate moving average
        windows = [
            np.mean(values[i:i+window_size])
            for i in range(0, len(values)-window_size+1)
        ]
        
        if not windows:
            return {"slope": 0.0, "variance": 0.0}
            
        # Calculate trend slope
        x = np.arange(len(windows))
        slope = np.polyfit(x, windows, 1)[0]
        
        return {
            "slope": slope,
            "variance": np.var(windows)
        }
