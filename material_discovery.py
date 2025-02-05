# File: material_discovery.py

import pandas as pd
import numpy as np
from kaleidoscope_engine import KaleidoscopeEngine
import matplotlib.pyplot as plt

def test_material_discovery():
    print("Running Material Discovery Use Case...")
    
    # Simulate data for material properties
    data = pd.DataFrame({
        "strength": np.random.rand(150),
        "conductivity": np.random.rand(150),
        "flexibility": np.random.rand(150),
        "temperature_resistance": np.random.rand(150)
    })

    engine = KaleidoscopeEngine()
    engine.add_memory_bank("MaterialBank", capacity=15)

    # Process data
    processed_data = engine.process_data(data)
    clustered_data = engine.generate_clusters(processed_data, n_clusters=3)
    insights = engine.validate_insights(clustered_data)

    # Visualize material clusters
    plt.scatter(processed_data['strength'], processed_data['conductivity'], alpha=0.7, c=clustered_data['cluster'])
    plt.title("Material Clusters Visualization")
    plt.xlabel("Strength")
    plt.ylabel("Conductivity")
    plt.grid(True)
    plt.show()

    print("Material Discovery Insights:", insights)

if __name__ == "__main__":
    test_material_discovery()
