class QuantumInterface:
    """Interactive interface for quantum molecular system."""
    
    def __init__(self):
        self.system = IntegratedQuantumSystem()
        self.current_molecule = None
        self.current_reaction = None
        
    def run(self):
        while True:
            self._display_menu()
            choice = input("\nEnter choice: ").strip()
            
            try:
                if choice == '1':
                    self._analyze_molecule()
                elif choice == '2':
                    self._simulate_reaction()
                elif choice == '3':
                    self._visualize_entanglement()
                elif choice == '4':
                    self._analyze_reaction_kinetics()
                elif choice == '5':
                    self._export_results()
                elif choice == '6':
                    print("Exiting...")
                    break
                else:
                    print("Invalid choice. Please try again.")
                    
            except Exception as e:
                print(f"Error: {str(e)}")
                
    def _analyze_molecule(self):
        """Interface for molecular analysis."""
        print("\nMolecular Analysis")
        print("=================")
        
        # Get molecular structure
        atoms = self._input_molecular_structure()
        
        # Perform analysis
        properties = self.system.analyze_molecule(
            atomic_positions=atoms['positions'],
            atomic_numbers=atoms['atomic_numbers']
        )
        
        # Display results
        self._display_molecular_properties(properties)
        
    def _simulate_reaction(self):
        """Interface for reaction simulation."""
        print("\nReaction Simulation")
        print("==================")
        
        # Get reactants and products
        reactants = self._input_molecular_structure("reactants")
        products = self._input_molecular_structure("products")
        
        # Simulate reaction
        self.system.simulate_reaction(
            reactants=reactants['positions'],
            products=products['positions']
        )
        
    def _visualize_entanglement(self):
        """Interface for entanglement visualization."""
        if not self.current_molecule:
            print("Please analyze a molecule first.")
            return
            
        print("\nEntanglement Visualization")
        print("=========================")
        
        # Get quantum state
        state = self._get_quantum_state()
        
        # Visualize entanglement
        self.system.entanglement_visualizer.visualize_entanglement(
            state_vector=state,
            basis_states=self._get_basis_states()
        )
        
    def _analyze_reaction_kinetics(self):
        """Interface for reaction kinetics analysis."""
        if not self.current_reaction:
            print("Please simulate a reaction first.")
            return
            
        print("\nReaction Kinetics Analysis")
        print("=========================")
        
        # Get temperature
        temperature = float(input("Enter temperature (K): "))
        
        # Calculate rates
        rate = self.system.reaction_analyzer.calculate_reaction_rate(temperature)