perspective_engine/simulation/scenario_generator.py
Python

import numpy as np

class ScenarioGenerator:
    def __init__(self, dimensions: int, num_scenarios: int = 10):
        self.dimensions = dimensions
        self.num_scenarios = num_scenarios
        self.scenarios = []

    def generate_scenarios(self, initial_conditions: dict, steps: int) -> list:
        """Generate multiple scenarios based on initial conditions and simulation steps."""
        self.scenarios = []  # Clear previous scenarios

        for _ in range(self.num_scenarios):
            scenario = self._generate_single_scenario(initial_conditions, steps)
            self.scenarios.append(scenario)

        return self.scenarios

    def _generate_single_scenario(self, initial_conditions: dict, steps: int) -> list:
      """Generate a single simulation scenario."""
      scenario = [initial_conditions]
      current_state = initial_conditions.copy()

      for _ in range(steps):
          next_state = self._calculate_next_state(current_state)
          scenario.append(next_state)
          current_state = next_state

      return scenario

    def _calculate_next_state(self, current_state: dict) -> dict:
        """Calculate the next state based on the current state."""
        next_state = current_state.copy()

        # Example: Simple stochastic evolution of dimensions
        for dim in range(self.dimensions):
            if f"dim_{dim}_value" in next_state:
                # Apply a random walk with a tendency to return to the initial value
                random_change = np.random.normal(0, 0.1)  # Gaussian noise
                tendency = 0.05 * (initial_conditions[f"dim_{dim}_value"] - next_state[f"dim_{dim}_value"])
                next_state[f"dim_{dim}_value"] += random_change + tendency

        return next_state

    def analyze_scenarios(self) -> dict:
        """Analyze generated scenarios to find common patterns or divergent outcomes."""
        if not self.scenarios:
            return {}

        # Example analysis: Calculate average and standard deviation for each dimension at each step
        analysis = {}
        for step in range(len(self.scenarios[0])):
            step_data = {f"dim_{dim}_avg": [] for dim in range(self.dimensions)}
            for scenario in self.scenarios:
                for dim in range(self.dimensions):
                    if f"dim_{dim}_value" in scenario[step]:
                        step_data[f"dim_{dim}_avg"].append(scenario[step][f"dim_{dim}_value"])

            for dim in range(self.dimensions):
                if step_data[f"dim_{dim}_avg"]:
                    analysis.setdefault(f"dim_{dim}_stats", []).append
                    analysis.setdefault(f"dim_{dim}_stats", []).append({
                        'step': step,
                        'avg': np.mean(step_data[f"dim_{dim}_avg"]),
                        'std': np.std(step_data[f"dim_{dim}_avg"])
                    })

        return analysis

    def get_state(self) -> dict:
        """Return the current state of the scenario generator."""
        return {
            'dimensions': self.dimensions,
            'num_scenarios': self.num_scenarios,
            'scenarios': self.scenarios,
            'analysis': self.analyze_scenarios()
        }
