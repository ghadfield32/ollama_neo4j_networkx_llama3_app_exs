import networkx as nx
import matplotlib.pyplot as plt

def visualize_graph(graph, debug=False):
    """Generate a visual representation of the schema graph."""
    # Color nodes based on database source
    node_colors = ['skyblue' if graph.nodes[n]['db'] == 'example1' else 'orange' for n in graph.nodes]
    pos = nx.spring_layout(graph, k=0.5, iterations=50)
    
    # Create Matplotlib figure for Streamlit display
    fig, ax = plt.subplots(figsize=(16, 16))
    nx.draw(graph, pos, ax=ax, node_color=node_colors, with_labels=True, font_weight="bold", font_size=8)
    ax.set_title("Combined Database Schema Graph", fontsize=18)

    # Optionally display debug information
    if debug:
        print(f"Graph has {len(graph.nodes)} nodes and {len(graph.edges)} edges.")
    
    return fig

def main(debug=False):
    _, _, metadata1, metadata2 = setup_databases(debug)
    graph = construct_graph(metadata1, metadata2, debug=debug)
    visualize_graph(graph, debug)

if __name__ == "__main__":
    main(debug=True)
