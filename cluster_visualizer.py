import networkx as nx
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np

def cluster_and_visualize(insights):
    """Clusters insights and visualizes relationships."""
    # Generate embeddings (simulated for simplicity)
    embeddings = np.random.rand(len(insights), 3)

    # Apply clustering
    kmeans = KMeans(n_clusters=3)
    labels = kmeans.fit_predict(embeddings)

    # Build graph
    G = nx.Graph()
    for i, insight in enumerate(insights):
        G.add_node(f"Node {i+1}", label=insight, cluster=labels[i])

    # Add edges between nodes in the same cluster
    for i, node1 in enumerate(G.nodes()):
        for j, node2 in enumerate(G.nodes()):
            if i != j and G.nodes[node1]["cluster"] == G.nodes[node2]["cluster"]:
                G.add_edge(node1, node2)

    # Visualize
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color=labels, cmap=plt.cm.viridis)
    plt.title("Clustered Insights Visualization")
    plt.show()
