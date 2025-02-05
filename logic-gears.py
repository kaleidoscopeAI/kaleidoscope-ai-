from __future__ import annotations
import numpy as np
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
import asyncio
import logging
from datetime import datetime

from ..nodes.base_node import BaseNode
from ..memory.pathways import PathwayManager
from ...utils.validation import validate_gear_operation

logger = logging.getLogger(__name__)

@dataclass
class LogicGear:
    gear_id: str
    specialization: str
    weight: float = 1.0
    active: bool = True
    connected_gears: Set[str] = field(default_factory=set)
    processing_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    operations_count: int = 0
    last_active: datetime = field(default_factory=datetime.now)

class LogicGearSystem:
    def __init__(
        self,
        pathway_manager: PathwayManager,
        num_gears: int = 40
    ):
        self.pathway_manager = pathway_manager
        self.gears: Dict[str, LogicGear] = {}
        self.gear_connections: Dict[str, Set[str]] = {}
        self._initialize_gears(num_gears)

    def _initialize_gears(self, num_gears: int):
        specializations = [
            "pattern_recognition",
            "data_transformation",
            "memory_integration",
            "decision_making",
            "learning_optimization"
        ]
        
        for i in range(num_gears):
            gear_id = f"gear_{i}"
            spec = specializations[i % len(specializations)]
            
            self.gears[gear_id] = LogicGear(
                gear_id=gear_id,
                specialization=spec,
                weight=np.random.uniform(0.5, 1.5)
            )
        
        self._establish_gear_connections()

    def _establish_gear_connections(self):
        """Creates initial connections between gears."""
        gear_ids = list(self.gears.keys())
        
        for gear_id in gear_ids:
            # Connect each gear to 2-4 others
            num_connections = np.random.randint(2, 5)
            potential_connections = [id for id in gear_ids if id != gear_id]
            
            if potential_connections:
                connections = set(np.random.choice(
                    potential_connections,
                    size=min(num_connections, len(potential_connections)),
                    replace=False
                ))
                
                self.gears[gear_id].connected_gears = connections
                
                # Create reciprocal connections
                for connected_id in connections:
                    self.gears[connected_id].connected_gears.add(gear_id)

    async def process_data(
        self,
        data: Dict[str, Any],
        source_gear: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Processes data through the gear system."""
        if not source_gear:
            source_gear = self._select_entry_gear(data)

        processed_results = []
        visited_gears = set()
        
        async def process_through_gear(gear_id: str, current_data: Dict):
            if gear_id in visited_gears:
                return
            
            visited_gears.add(gear_id)
            gear = self.gears[gear_id]
            
            # Process data through current gear
            result = await self._process_in_gear(gear, current_data)
            if result:
                processed_results.append(result)
                
                # Propagate to connected gears
                for connected_id in gear.connected_gears:
                    if connected_id not in visited_gears:
                        await process_through_gear(connected_id, result)

        # Start processing from source gear
        await process_through_gear(source_gear, data)
        return processed_results

    async def _process_in_gear(
        self,
        gear: LogicGear,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Processes data within a specific gear."""
        try:
            # Apply gear's specialization
            if gear.specialization == "pattern_recognition":
                result = await self._recognize_patterns(gear, data)
            elif gear.specialization == "data_transformation":
                result = await self._transform_data(gear, data)
            elif gear.specialization == "memory_integration":
                result = await self._integrate_memory(gear, data)
            elif gear.specialization == "decision_making":
                result = await self._make_decision(gear, data)
            elif gear.specialization == "learning_optimization":
                result = await self._optimize_learning(gear, data)
            else:
                result = await self._default_processing(gear, data)

            if result:
                # Update gear metrics
                gear.operations_count += 1
                gear.last_active = datetime.now()
                
                # Validate result
                if validate_gear_operation(result):
                    return result
                    
            return None

        except Exception as e:
            logger.error(f"Gear processing error in {gear.gear_id}: {str(e)}")
            return None

    async def _recognize_patterns(
        self,
        gear: LogicGear,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Recognizes patterns in data."""
        patterns = []
        confidence_scores = []
        
        try:
            # Extract numerical patterns
            if isinstance(data.get("values"), (list, np.ndarray)):
                num_pattern = self._find_numerical_patterns(data["values"])
                if num_pattern:
                    patterns.append(num_pattern)
                    confidence_scores.append(num_pattern["confidence"])

            # Extract structural patterns
            if isinstance(data.get("structure"), dict):
                struct_pattern = self._find_structural_patterns(data["structure"])
                if struct_pattern:
                    patterns.append(struct_pattern)
                    confidence_scores.append(struct_pattern["confidence"])

            # Extract temporal patterns
            if "timestamp" in data:
                temp_pattern = self._find_temporal_patterns(data)
                if temp_pattern:
                    patterns.append(temp_pattern)
                    confidence_scores.append(temp_pattern["confidence"])

            if patterns:
                return {
                    "type": "pattern_recognition",
                    "gear_id": gear.gear_id,
                    "patterns": patterns,
                    "confidence": np.mean(confidence_scores),
                    "timestamp": datetime.now().isoformat()
                }

            return None

        except Exception as e:
            logger.error(f"Pattern recognition error: {str(e)}")
            return None

    async def _transform_data(
        self,
        gear: LogicGear,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Transforms data using the gear's specialization."""
        try:
            transformed_data = {}
            
            # Transform numerical values
            if isinstance(data.get("values"), (list, np.ndarray)):
                values = np.array(data["values"])
                transformed_data["normalized"] = self._normalize_values(values)
                transformed_data["encoded"] = self._encode_values(values)

            # Transform structures
            if isinstance(data.get("structure"), dict):
                transformed_data["structure"] = self._transform_structure(
                    data["structure"]
                )

            # Transform sequences
            if isinstance(data.get("sequence"), list):
                transformed_data["sequence"] = self._transform_sequence(
                    data["sequence"]
                )

            return {
                "type": "data_transformation",
                "gear_id": gear.gear_id,
                "transformed_data": transformed_data,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Data transformation error: {str(e)}")
            return None

    async def _integrate_memory(
        self,
        gear: LogicGear,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Integrates data with memory system."""
        try:
            # Create memory pathways
            pathway_ids = []
            for key, value in data.items():
                if isinstance(value, dict):
                    pathway_id = await self.pathway_manager.create_pathway(
                        source_id=gear.gear_id,
                        target_id="memory_bank",
                        pathway_type="integration",
                        weight=gear.weight
                    )
                    if pathway_id:
                        pathway_ids.append(pathway_id)

            # Send data through pathways
            integration_results = []
            for pathway_id in pathway_ids:
                result = await self.pathway_manager.send_data(
                    data=data,
                    source_id=gear.gear_id,
                    target_id="memory_bank",
                    priority=gear.weight
                )
                if result:
                    integration_results.append(result)

            return {
                "type": "memory_integration",
                "gear_id": gear.gear_id,
                "pathways": pathway_ids,
                "integration_results": integration_results,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Memory integration error: {str(e)}")
            return None

    async def _make_decision(
        self,
        gear: LogicGear,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Makes decisions based on processed data."""
        try:
            decisions = []
            confidences = []

            # Analyze available evidence
            evidence = self._gather_evidence(data)
            if evidence:
                # Generate decision candidates
                candidates = self._generate_decision_candidates(evidence)
                
                # Evaluate each candidate
                for candidate in candidates:
                    evaluation = self._evaluate_decision(candidate, evidence)
                    if evaluation["confidence"] > 0.5:
                        decisions.append(evaluation["decision"])
                        confidences.append(evaluation["confidence"])

            if decisions:
                return {
                    "type": "decision_making",
                    "gear_id": gear.gear_id,
                    "decisions": decisions,
                    "confidence": np.mean(confidences),
                    "evidence": evidence,
                    "timestamp": datetime.now().isoformat()
                }

            return None

        except Exception as e:
            logger.error(f"Decision making error: {str(e)}")
            return None

    async def _optimize_learning(
        self,
        gear: LogicGear,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Optimizes learning parameters based on processing results."""
        try:
            # Extract performance metrics
            metrics = self._extract_performance_metrics(data)
            
            # Calculate optimal parameters
            optimized_params = self._calculate_optimal_parameters(metrics)
            
            # Generate optimization directives
            directives = []
            for param, value in optimized_params.items():
                if self._should_apply_optimization(param, value, metrics):
                    directives.append({
                        "parameter": param,
                        "value": value,
                        "confidence": metrics.get(f"{param}_confidence", 0.5)
                    })

            if directives:
                return {
                    "type": "learning_optimization",
                    "gear_id": gear.gear_id,
                    "directives": directives,
                    "metrics": metrics,
                    "timestamp": datetime.now().isoformat()
                }

            return None

        except Exception as e:
            logger.error(f"Learning optimization error: {str(e)}")
            return None

    def _select_entry_gear(self, data: Dict[str, Any]) -> str:
        """Selects the most appropriate gear for initial processing."""
        try:
            # Calculate suitability scores
            scores = {}
            for gear_id, gear in self.gears.items():
                score = self._calculate_gear_suitability(gear, data)
                scores[gear_id] = score

            # Select gear with highest score
            return max(scores.items(), key=lambda x: x[1])[0]

        except Exception as e:
            logger.error(f"Entry gear selection error: {str(e)}")
            return list(self.gears.keys())[0]

    def _calculate_gear_suitability(
        self,
        gear: LogicGear,
        data: Dict[str, Any]
    ) -> float:
        """Calculates how suitable a gear is for processing specific data."""
        try:
            score = gear.weight
            
            # Check specialization match
            if gear.specialization == "pattern_recognition":
                if "values" in data or "sequence" in data:
                    score *= 1.5
            elif gear.specialization == "data_transformation":
                if "values" in data or "structure" in data:
                    score *= 1.5
            elif gear.specialization == "memory_integration":
                if "structure" in data or "references" in data:
                    score *= 1.5
            elif gear.specialization == "decision_making":
                if "evidence" in data or "options" in data:
                    score *= 1.5
            elif gear.specialization == "learning_optimization":
                if "metrics" in data or "performance" in data:
                    score *= 1.5

            # Consider gear activity
            time_since_active = (datetime.now() - gear.last_active).total_seconds()
            activity_factor = 1.0 / (1.0 + time_since_active / 3600)  # 1-hour scale
            score *= activity_factor

            return score

        except Exception as e:
            logger.error(f"Gear suitability calculation error: {str(e)}")
            return 0.0