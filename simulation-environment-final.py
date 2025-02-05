def _get_nearby_nodes(self, node_id: str, radius: float = 10.0) -> Set[str]:
        """Gets nodes within a certain radius using spatial index."""
        try:
            position = self.node_positions[node_id]
            cell_size = 10.0
            
            # Calculate grid cells to check
            cell_radius = int(np.ceil(radius / cell_size))
            base_cell = tuple(int(p / cell_size) for p in position)
            
            nearby_nodes = set()
            
            # Check neighboring cells
            for dx in range(-cell_radius, cell_radius + 1):
                for dy in range(-cell_radius, cell_radius + 1):
                    for dz in range(-cell_radius, cell_radius + 1):
                        cell = (
                            base_cell[0] + dx,
                            base_cell[1] + dy,
                            base_cell[2] + dz
                        )
                        
                        if cell in self.spatial_index:
                            # Check actual distances for nodes in this cell
                            for other_id in self.spatial_index[cell]:
                                if other_id != node_id:
                                    dist = np.linalg.norm(
                                        self.node_positions[other_id] - position
                                    )
                                    if dist <= radius:
                                        nearby_nodes.add(other_id)
                                        
            return nearby_nodes
            
        except Exception as e:
            logger.error(f"Nearby nodes lookup error: {str(e)}")
            return set()

    async def simulate_evolution(self, generations: int = 10) -> Dict[str, Any]:
        """Simulates evolutionary processes over multiple generations."""
        evolution_metrics = {
            "generations": [],
            "population_size": [],
            "average_fitness": [],
            "best_fitness": [],
            "trait_distribution": []
        }

        try:
            for generation in range(generations):
                logger.info(f"Starting evolution generation {generation + 1}")
                
                # Evaluate fitness of all nodes
                fitness_scores = await self._evaluate_population_fitness()
                
                # Select nodes for reproduction
                selected_nodes = self._select_for_reproduction(fitness_scores)
                
                # Create next generation
                await self._create_next_generation(selected_nodes)
                
                # Record metrics
                gen_metrics = self._calculate_generation_metrics(fitness_scores)
                evolution_metrics["generations"].append(generation + 1)
                evolution_metrics["population_size"].append(len(self.nodes))
                evolution_metrics["average_fitness"].append(gen_metrics["avg_fitness"])
                evolution_metrics["best_fitness"].append(gen_metrics["best_fitness"])
                evolution_metrics["trait_distribution"].append(
                    gen_metrics["trait_distribution"]
                )
                
                logger.info(f"Completed evolution generation {generation + 1}")
                
            return evolution_metrics
            
        except Exception as e:
            logger.error(f"Evolution simulation error: {str(e)}")
            return evolution_metrics

    async def _evaluate_population_fitness(self) -> Dict[str, float]:
        """Evaluates fitness of all nodes in the population."""
        fitness_scores = {}
        
        try:
            for node_id, node in self.nodes.items():
                # Calculate fitness components
                interaction_success = self._calculate_interaction_success(node_id)
                energy_efficiency = self._calculate_energy_efficiency(node_id)
                adaptation_score = self._calculate_adaptation_score(node_id)
                
                # Combine components into final fitness
                fitness = (
                    0.4 * interaction_success +
                    0.3 * energy_efficiency +
                    0.3 * adaptation_score
                )
                
                fitness_scores[node_id] = fitness
                
            return fitness_scores
            
        except Exception as e:
            logger.error(f"Fitness evaluation error: {str(e)}")
            return fitness_scores

    def _calculate_interaction_success(self, node_id: str) -> float:
        """Calculates interaction success rate for a node."""
        try:
            # Get recent interactions involving this node
            node_interactions = [
                r for r in self.reaction_history[-100:]  # Look at last 100 reactions
                if node_id in (r["node1_id"], r["node2_id"])
            ]
            
            if not node_interactions:
                return 0.0
                
            # Calculate success rate
            successful = sum(
                1 for r in node_interactions
                if r.get("result", {}).get("success", False)
            )
            
            return successful / len(node_interactions)
            
        except Exception as e:
            logger.error(f"Interaction success calculation error: {str(e)}")
            return 0.0

    def _calculate_energy_efficiency(self, node_id: str) -> float:
        """Calculates energy efficiency score for a node."""
        try:
            node = self.nodes[node_id]
            
            # Calculate energy usage efficiency
            energy_delta = node.state.energy - 100.0  # Assuming initial energy of 100
            interactions = len([
                r for r in self.reaction_history[-100:]
                if node_id in (r["node1_id"], r["node2_id"])
            ])
            
            if interactions == 0:
                return 0.0
                
            # Higher score for maintaining energy while interacting
            efficiency = 1.0 - abs(energy_delta) / (100.0 * interactions)
            
            return max(0.0, efficiency)
            
        except Exception as e:
            logger.error(f"Energy efficiency calculation error: {str(e)}")
            return 0.0

    def _calculate_adaptation_score(self, node_id: str) -> float:
        """Calculates how well a node has adapted to environmental conditions."""
        try:
            node = self.nodes[node_id]
            position = self.node_positions[node_id]
            
            # Get local conditions
            local_conditions = self._get_local_conditions(position)
            
            # Calculate adaptation to temperature
            temp_adaptation = np.exp(
                -abs(local_conditions["temperature"] - 298.15) / 100
            )
            
            # Calculate adaptation to chemical environment
            chemical_adaptation = self._calculate_chemical_adaptation(
                node_id,
                local_conditions
            )
            
            # Calculate adaptation to energy field
            field_adaptation = self._calculate_field_adaptation(
                node_id,
                local_conditions
            )
            
            # Combine adaptation scores
            adaptation = (
                0.4 * temp_adaptation +
                0.3 * chemical_adaptation +
                0.3 * field_adaptation
            )
            
            return adaptation
            
        except Exception as e:
            logger.error(f"Adaptation score calculation error: {str(e)}")
            return 0.0

    def _calculate_chemical_adaptation(
        self,
        node_id: str,
        conditions: Dict[str, Any]
    ) -> float:
        """Calculates adaptation to chemical environment."""
        try:
            node = self.nodes[node_id]
            
            if not conditions.get("chemical_concentrations"):
                return 1.0
                
            adaptations = []
            for chemical, concentration in conditions["chemical_concentrations"].items():
                # Check if node has corresponding trait
                trait_value = node.dna.traits.get(f"chemical_resistance_{chemical}", 0.5)
                
                # Calculate adaptation to this chemical
                adaptation = np.exp(-concentration * (1.0 - trait_value))
                adaptations.append(adaptation)
                
            return np.mean(adaptations) if adaptations else 1.0
            
        except Exception as e:
            logger.error(f"Chemical adaptation calculation error: {str(e)}")
            return 0.0

    def _calculate_field_adaptation(
        self,
        node_id: str,
        conditions: Dict[str, Any]
    ) -> float:
        """Calculates adaptation to energy field."""
        try:
            node = self.nodes[node_id]
            field_strength = conditions.get("field_strength", 0.0)
            
            # Check field response trait
            field_response = node.dna.traits.get("field_response", 0.5)
            
            # Calculate adaptation
            adaptation = np.exp(-field_strength * (1.0 - field_response))
            
            return adaptation
            
        except Exception as e:
            logger.error(f"Field adaptation calculation error: {str(e)}")
            return 0.0

    def _select_for_reproduction(
        self,
        fitness_scores: Dict[str, float]
    ) -> List[str]:
        """Selects nodes for reproduction using tournament selection."""
        try:
            selected_nodes = []
            population = list(fitness_scores.keys())
            
            if not population:
                return selected_nodes
                
            # Number of nodes to select
            selection_count = len(population) // 2
            
            # Tournament selection
            tournament_size = 3
            for _ in range(selection_count):
                # Select random tournament participants
                tournament = np.random.choice(
                    population,
                    size=min(tournament_size, len(population)),
                    replace=False
                )
                
                # Select winner
                winner = max(
                    tournament,
                    key=lambda x: fitness_scores.get(x, 0.0)
                )
                selected_nodes.append(winner)
                
            return selected_nodes
            
        except Exception as e:
            logger.error(f"Selection error: {str(e)}")
            return []

    async def _create_next_generation(self, selected_nodes: List[str]):
        """Creates the next generation of nodes through reproduction."""
        try:
            # Clear non-selected nodes
            for node_id in list(self.nodes.keys()):
                if node_id not in selected_nodes:
                    await self._remove_node(node_id)

            # Create offspring
            new_nodes = []
            for parent_id in selected_nodes:
                try:
                    # Create offspring through replication
                    offspring = await self.nodes[parent_id].replicate()
                    if offspring:
                        new_nodes.append(offspring)
                        
                        # Add offspring to simulation
                        await self.add_node(
                            offspring,
                            position=self.node_positions[parent_id] + np.random.randn(3)
                        )
                except Exception as e:
                    logger.error(f"Offspring creation error: {str(e)}")

            logger.info(
                f"Created next generation: {len(new_nodes)} new nodes"
            )
            
        except Exception as e:
            logger.error(f"Next generation creation error: {str(e)}")

    async def _remove_node(self, node_id: str):
        """Removes a node from the simulation."""
        try:
            if node_id in self.nodes:
                del self.nodes[node_id]
            if node_id in self.node_positions:
                del self.node_positions[node_id]
            if node_id in self.node_velocities:
                del self.node_velocities[node_id]
                
            # Update spatial index
            for cell in self.spatial_index.values():
                if node_id in cell:
                    cell.remove(node_id)
                    
        except Exception as e:
            logger.error(f"Node removal error: {str(e)}")

    def _calculate_generation_metrics(
        self,
        fitness_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculates metrics for the current generation."""
        try:
            if not fitness_scores:
                return {
                    "avg_fitness": 0.0,
                    "best_fitness": 0.0,
                    "trait_distribution": {}
                }

            # Calculate fitness metrics
            avg_fitness = np.mean(list(fitness_scores.values()))
            best_fitness = max(fitness_scores.values())
            
            # Calculate trait distribution
            trait_distribution = {}
            for node in self.nodes.values():
                for trait, value in node.dna.traits.items():
                    if trait not in trait_distribution:
                        trait_distribution[trait] = []
                    trait_distribution[trait].append(value)
                    
            # Calculate average trait values
            trait_distribution = {
                trait: np.mean(values)
                for trait, values in trait_distribution.items()
            }
            
            return {
                "avg_fitness": avg_fitness,
                "best_fitness": best_fitness,
                "trait_distribution": trait_distribution
            }
            
        except Exception as e:
            logger.error(f"Generation metrics calculation error: {str(e)}")
            return {
                "avg_fitness": 0.0,
                "best_fitness": 0.0,
                "trait_distribution": {}
            }

    async def get_simulation_status(self) -> Dict[str, Any]:
        """Returns current status of the simulation environment."""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "node_count": len(self.nodes),
                "total_energy": sum(node.state.energy for node in self.nodes.values()),
                "average_fitness": np.mean([
                    node.dna.traits.get("fitness", 0.0)
                    for node in self.nodes.values()
                ]) if self.nodes else 0.0,
                "environmental_conditions": self.conditions.to_dict(),
                "metrics": {
                    "step_count": self.metrics.step_count,
                    "total_interactions": self.metrics.node_interactions,
                    "success_rate": (
                        self.metrics.successful_reactions /
                        max(1, self.metrics.successful_reactions + self.metrics.failed_reactions)
                    ),
                    "stability_score": self.metrics.stability_score
                }
            }
            
        except Exception as e:
            logger.error(f"Status retrieval error: {str(e)}")
            return {}