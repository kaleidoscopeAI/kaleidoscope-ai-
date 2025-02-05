from __future__ import annotations
import numpy as np
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import asyncio
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from .kaleidoscope_engine import KaleidoscopeEngine
from ..nodes.pure_node import PureNode
from ...memory.graph import MemoryGraph

logger = logging.getLogger(__name__)

@dataclass
class ProcessingMirror:
    mirror_id: str
    engine: KaleidoscopeEngine
    active_tasks: Set[str] = field(default_factory=set)
    results_cache: Dict[str, Any] = field(default_factory=dict)
    last_sync: datetime = field(default_factory=datetime.now)
    sync_status: float = 1.0

class MirroredEngine:
    def __init__(
        self,
        num_mirrors: int = 3,
        memory_graph: Optional[MemoryGraph] = None
    ):
        self.mirrors: Dict[str, ProcessingMirror] = {}
        self.memory_graph = memory_graph or MemoryGraph()
        self.thread_pool = ThreadPoolExecutor(max_workers=num_mirrors * 2)
        self.validation_threshold = 0.8
        
        # Initialize processing mirrors
        for i in range(num_mirrors):
            self._create_mirror(f"mirror_{i}")

    def _create_mirror(self, mirror_id: str):
        engine = KaleidoscopeEngine(
            num_logic_gears=40,
            memory_graph=self.memory_graph
        )
        self.mirrors[mirror_id] = ProcessingMirror(
            mirror_id=mirror_id,
            engine=engine
        )

    async def process_data(
        self,
        data: Dict[str, Any],
        validation_required: bool = True
    ) -> Optional[Dict[str, Any]]:
        task_id = f"task_{datetime.now().timestamp()}"
        mirror_results = []

        # Process in all mirrors
        for mirror in self.mirrors.values():
            mirror.active_tasks.add(task_id)
            try:
                result = await self._process_in_mirror(mirror, data)
                if result:
                    mirror_results.append((mirror.mirror_id, result))
            finally:
                mirror.active_tasks.remove(task_id)

        if not mirror_results:
            return None

        # Validate and combine results
        if validation_required and len(mirror_results) > 1:
            return await self._validate_results(mirror_results)
        else:
            return mirror_results[0][1]

    async def _process_in_mirror(
        self,
        mirror: ProcessingMirror,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        try:
            result = await mirror.engine.process_data(data)
            if result:
                mirror.results_cache[str(hash(str(data)))] = result
                mirror.last_sync = datetime.now()
            return result
        except Exception as e:
            logger.error(f"Mirror processing error in {mirror.mirror_id}: {str(e)}")
            mirror.sync_status *= 0.9
            return None

    async def _validate_results(
        self,
        results: List[Tuple[str, Dict[str, Any]]]
    ) -> Optional[Dict[str, Any]]:
        try:
            # Calculate similarity scores
            similarity_matrix = np.zeros((len(results), len(results)))
            for i, (_, result1) in enumerate(results):
                for j, (_, result2) in enumerate(results):
                    if i != j:
                        similarity_matrix[i][j] = self._calculate_similarity(
                            result1,
                            result2
                        )

            # Find most consistent result
            avg_similarities = np.mean(similarity_matrix, axis=1)
            most_consistent_idx = np.argmax(avg_similarities)
            
            if avg_similarities[most_consistent_idx] >= self.validation_threshold:
                validated_result = results[most_consistent_idx][1]
                await self._update_mirror_states(
                    results,
                    most_consistent_idx,
                    avg_similarities
                )
                return validated_result
            else:
                logger.warning("Validation failed: insufficient result consistency")
                return await self._handle_validation_failure(results)

        except Exception as e:
            logger.error(f"Result validation error: {str(e)}")
            return results[0][1]  # Return first result as fallback

    def _calculate_similarity(
        self,
        result1: Dict[str, Any],
        result2: Dict[str, Any]
    ) -> float:
        try:
            if not result1 or not result2:
                return 0.0

            similarities = []
            
            # Compare processed data
            if "processed_data" in result1 and "processed_data" in result2:
                data_similarity = self._compare_data_structures(
                    result1["processed_data"],
                    result2["processed_data"]
                )
                similarities.append(data_similarity)

            # Compare insights
            if "insights" in result1 and "insights" in result2:
                insight_similarity = self._compare_insights(
                    result1["insights"],
                    result2["insights"]
                )
                similarities.append(insight_similarity)

            # Compare metrics
            if "metrics" in result1 and "metrics" in result2:
                metric_similarity = self._compare_metrics(
                    result1["metrics"],
                    result2["metrics"]
                )
                similarities.append(metric_similarity)

            return np.mean(similarities) if similarities else 0.0

        except Exception as e:
            logger.error(f"Similarity calculation error: {str(e)}")
            return 0.0

    def _compare_data_structures(
        self,
        data1: Any,
        data2: Any,
        depth: int = 0,
        max_depth: int = 5
    ) -> float:
        if depth >= max_depth:
            return 1.0 if data1 == data2 else 0.0

        if type(data1) != type(data2):
            return 0.0

        if isinstance(data1, dict):
            if not data1 or not data2:
                return 1.0 if data1 == data2 else 0.0
                
            similarities = []
            for key in set(data1.keys()) & set(data2.keys()):
                similarity = self._compare_data_structures(
                    data1[key],
                    data2[key],
                    depth + 1
                )
                similarities.append(similarity)
            return np.mean(similarities) if similarities else 0.0

        elif isinstance(data1, (list, tuple)):
            if not data1 or not data2:
                return 1.0 if data1 == data2 else 0.0
                
            similarities = []
            for item1, item2 in zip(data1, data2):
                similarity = self._compare_data_structures(
                    item1,
                    item2,
                    depth + 1
                )
                similarities.append(similarity)
            return np.mean(similarities) if similarities else 0.0

        elif isinstance(data1, (int, float)):
            try:
                diff = abs(data1 - data2)
                max_val = max(abs(data1), abs(data2))
                return 1.0 - (diff / max_val) if max_val > 0 else 1.0
            except:
                return 0.0

        else:
            return 1.0 if data1 == data2 else 0.0

    def _compare_insights(
        self,
        insights1: List[Dict[str, Any]],
        insights2: List[Dict[str, Any]]
    ) -> float:
        if not insights1 or not insights2:
            return 1.0 if insights1 == insights2 else 0.0

        # Match insights by ID or content similarity
        matched_pairs = []
        unmatched1 = set(range(len(insights1)))
        unmatched2 = set(range(len(insights2)))

        # First pass: match by ID
        for i in unmatched1.copy():
            for j in unmatched2.copy():
                if insights1[i].get("id") == insights2[j].get("id"):
                    matched_pairs.append((i, j))
                    unmatched1.remove(i)
                    unmatched2.remove(j)
                    break

        # Second pass: match by content similarity
        for i in unmatched1.copy():
            best_match = None
            best_similarity = 0.0
            for j in unmatched2:
                similarity = self._compare_data_structures(
                    insights1[i],
                    insights2[j]
                )
                if similarity > best_similarity and similarity > 0.8:
                    best_similarity = similarity
                    best_match = j
            
            if best_match is not None:
                matched_pairs.append((i, best_match))
                unmatched1.remove(i)
                unmatched2.remove(best_match)

        # Calculate overall similarity
        if not matched_pairs:
            return 0.0

        similarities = []
        for i, j in matched_pairs:
            similarity = self._compare_data_structures(
                insights1[i],
                insights2[j]
            )
            similarities.append(similarity)

        return np.mean(similarities)

    def _compare_metrics(
        self,
        metrics1: Dict[str, Any],
        metrics2: Dict[str, Any]
    ) -> float:
        if not metrics1 or not metrics2:
            return 1.0 if metrics1 == metrics2 else 0.0

        similarities = []
        common_keys = set(metrics1.keys()) & set(metrics2.keys())
        
        for key in common_keys:
            value1 = metrics1[key]
            value2 = metrics2[key]
            
            if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                try:
                    max_val = max(abs(value1), abs(value2))
                    if max_val == 0:
                        similarities.append(1.0 if value1 == value2 else 0.0)
                    else:
                        diff = abs(value1 - value2)
                        similarities.append(1.0 - (diff / max_val))
                except:
                    similarities.append(0.0)
            else:
                similarities.append(
                    1.0 if value1 == value2 else 0.0
                )

        return np.mean(similarities) if similarities else 0.0

    async def _update_mirror_states(
        self,
        results: List[Tuple[str, Dict[str, Any]]],
        validated_idx: int,
        similarities: np.ndarray
    ):
        validated_mirror_id = results[validated_idx][0]
        
        for i, (mirror_id, _) in enumerate(results):
            mirror = self.mirrors[mirror_id]
            if mirror_id == validated_mirror_id:
                mirror.sync_status = min(1.0, mirror.sync_status * 1.1)
            else:
                mirror.sync_status *= max(0.5, similarities[i])

            if mirror.sync_status < 0.5:
                await self._resync_mirror(mirror, validated_mirror_id)

    async def _resync_mirror(
        self,
        mirror: ProcessingMirror,
        reference_mirror_id: str
    ):
        try:
            reference_mirror = self.mirrors[reference_mirror_id]
            
            # Copy engine state
            mirror.engine = await self._clone_engine(reference_mirror.engine)
            
            # Clear caches
            mirror.results_cache.clear()
            mirror.active_tasks.clear()
            
            # Reset status
            mirror.sync_status = 0.8
            mirror.last_sync = datetime.now()
            
            logger.info(f"Resynced mirror {mirror.mirror_id}")
            
        except Exception as e:
            logger.error(f"Mirror resync error: {str(e)}")

    async def _clone_engine(
        self,
        source_engine: KaleidoscopeEngine
    ) -> KaleidoscopeEngine:
        """Creates a deep copy of an engine instance."""
        engine = KaleidoscopeEngine(
            num_logic_gears=len(source_engine.logic_gears),
            memory_graph=self.memory_graph
        )
        
        # Copy engine state
        engine.state = source_engine.state
        
        # Clone nodes
        for node_id, node in source_engine.nodes.items():
            engine.nodes[node_id] = await self._clone_node(node)
            
        return engine

    async def _clone_node(self, node: PureNode) -> PureNode:
        """Creates a deep copy of a node."""
        return PureNode(
            node_id=node.node_id,
            initial_dna=node.dna,
            entity_type=node.entity_type,
            parent_node=node.parent_node
        )

    async def _handle_validation_failure(
        self,
        results: List[Tuple[str, Dict[str, Any]]]
    ) -> Optional[Dict[str, Any]]:
        try:
            # Attempt to reconcile results
            reconciled_result = await self._reconcile_results(results)
            if reconciled_result:
                return reconciled_result

            # If reconciliation fails, use highest confidence result
            confidence_scores = []
            for _, result in results:
                confidence = self._calculate_result_confidence(result)
                confidence_scores.append(confidence)

            if confidence_scores:
                best_idx = np.argmax(confidence_scores)
                return results[best_idx][1]

            return None

        except Exception as e:
            logger.error(f"Validation failure handling error: {str(e)}")
            return None

    def _calculate_result_confidence(self, result: Dict[str, Any]) -> float:
        try:
            confidence_factors = []
            
            # Check processed data
            if "processed_data" in result:
                data_confidence = self._evaluate_data_confidence(
                    result["processed_data"]
                )
                confidence_factors.append(data_confidence)

            # Check insights
            if "insights" in result:
                insight_confidence = self._evaluate_insight_confidence(
                    result["insights"]
                )
                confidence_factors.append(insight_confidence)

            # Check metrics
            if "metrics" in result:
                metric_confidence = self._evaluate_metric_confidence(
                    result["metrics"]
                )
                confidence_factors.append(metric_confidence)

            return np.mean(confidence_factors) if confidence_factors else 0.0

        except Exception as e:
            logger.error(f"Confidence calculation error: {str(e)}")
            return 0.0