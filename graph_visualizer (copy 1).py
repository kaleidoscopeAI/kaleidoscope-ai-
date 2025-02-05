import networkx as nx
import plotly.graph_objects as go

def visualize_graph(insights, iteration=1):
    """Visualizes insights as a graph."""
    G = nx.Graph()

    # Add nodes and edges based on insights
    for i, insight in enumerate(insights):
        node_id = f"Node_{i + 1}"
        G.add_node(node_id, label=insight)
        if i > 0:
            G.add_edge(f"Node_{i}", node_id)

    # Calculate layout
    pos = nx.spring_layout(G)

    # Prepare data for visualization
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(G.nodes[node]["label"])

    # Create the plot
    fig = go.Figure()

    # Add edges
    fig.add_trace(go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color="grey"),
        hoverinfo="none",
        mode="lines"
    ))

    # Add nodes
    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        marker=dict(size=10, color="blue", line_width=2),
        text=node_text,
        hoverinfo="text"
    ))

    # Configure layout
    fig.update_layout(
        title=f"Graph Visualization - Iteration {iteration}",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False)
    )

    # Save or display
    fig.show()
