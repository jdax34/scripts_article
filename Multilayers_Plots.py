from my_globals import *
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from networkx import edge_betweenness_centrality as betweenness
import os
from matplotlib.lines import Line2D  # Import for custom legend
import network_manipulation as nm

# Layer colors
layer_colors = {
    1: '#00008d',  # Blue for neuropsychological scores (top layer)
    2: '#006300',  # Green for subcortical damages (middle layer)
    3: '#fb0000'   # Red for cortical damages (bottom layer)
}


def get_z_pos(layer_index):
    # Mapping between the layer number (1,2,3) and its z position on output graph
    pos_layer_dict = {
        1:2,
        2:1,
        3:0
    }
    return pos_layer_dict.get(layer_index)

def get_path(layers,hemi,imp):
    if layers == [1,2,3]:
        return rf"{MAIN_PATH}\Coding\Correlation_Matrix\DECO_TESTS_DAMAGE\Spearman_Corr_Matrix_{hemi}_{imp}.csv"
    elif layers == [1, 2]: 
        return rf"{MAIN_PATH}\Coding\Correlation_Matrix\DECO_AND_TESTS\Spearman_Corr_Matrix_{hemi}_{imp}.csv"
    elif layers == [1, 3]: 
        return rf"{MAIN_PATH}\Coding\Correlation_Matrix\TESTS_AND_DAMAGE\Spearman_Corr_Matrix_{hemi}_{imp}.csv"
    elif layers == [2, 3]: 
        return rf"{MAIN_PATH}\Coding\Correlation_Matrix\DECO_AND_DAMAGE\Spearman_Corr_Matrix_{hemi}.csv"
    elif layers == [1]: 
        return rf"{MAIN_PATH}\Coding\Correlation_Matrix\TESTS\Spearman_Corr_Matrix_{hemi}_{imp}.csv"
    elif layers == [2]: 
        return rf"{MAIN_PATH}\Coding\Correlation_Matrix\DECO\Spearman_Corr_Matrix_{hemi}.csv"
    elif layers == [3]: 
        return rf"{MAIN_PATH}\Coding\Correlation_Matrix\DAMAGE\Spearman_Corr_Matrix_{hemi}.csv"
    else:
        print("Error: Wrong layers.")
        return 0

def get_nodes_from_layers(graph, layers):
    nodes = [node for node, data in graph.nodes(data=True) if data.get('layer') in set(layers)]
    return nodes

def get_extent(G_pos, pad=0.1):
    xyz = np.array(list(G_pos.values()))
    xmin, ymin, _ = np.min(xyz, axis=0)
    xmax, ymax, _ = np.max(xyz, axis=0)
    dx = xmax - xmin
    dy = ymax - ymin
    return (xmin - pad * dx, xmax + pad * dx), \
        (ymin - pad * dy, ymax + pad * dy)

def draw_planes(G_pos, layers_z, ax):
    # get the min and max {x,y} couples for each layer to define the square edges
    (xmin, xmax), (ymin, ymax)= get_extent(G_pos,0.1)
    u = np.linspace(xmin, xmax, 10)
    v = np.linspace(ymin, ymax, 10)
    U, V = np.meshgrid(u ,v)

    for z in layers_z:
        W = z * np.ones_like(U)
        # Use the layer color directly based on z-coordinate
        color = layer_colors.get(3-z, 'grey')  # z + 1 to match 1st, 2nd, 3rd layers correctly

        # Plot the surface with the correct color
        ax.plot_surface(U, V, W, color=color, alpha=0.2, zorder=1)
    
def most_central_edge(G):
    centrality = betweenness(G, weight="weight")
    return max(centrality, key=centrality.get)

def save_multilayers_plots(fig, legend_fig, hemi, imp, label, treshold):
    # Create file if it doesnt exist
    save_dir = rf"{MAIN_PATH}\Coding\Correlation_matrix\Multilayers_Plots\{treshold}\{hemi}\{label}"
    os.makedirs(save_dir, exist_ok=True)
    # Save plot
    plot_file_path = os.path.join(save_dir, f"Correlationplot_{label}_{hemi}_{imp}.png")
    fig.savefig(plot_file_path, dpi=300, bbox_inches='tight')

    # Save legend
    legend_file_path = os.path.join(save_dir, f"Correlationlegend_{label}_{hemi}_{imp}.png")
    legend_fig.savefig(legend_file_path, dpi=300, bbox_inches='tight')


def main() : 
    layers = [1,3]           # [1]  [2]  [3] [1,2]  [1,3]  [2,3]  [1,2,3]   

    label = nm.get_label(layers)

    for treshold in [0.175, 0.229]:    #, 0.229
        for hemi in ['L', 'R']:
            for imp in [1, 2, 3, 4, 5,'mean']:                # 1, 2, 3, 4, 5, 
                # Votre code ici

                                
                file_path = get_path(layers,hemi,imp)
                #Checking the file existence
                if not os.path.exists(file_path):
                    print(f"File does not exist in : {file_path}")
                    return 
                
                else:
                    # Read file in dataframe
                    df = pd.read_csv(file_path, delimiter=';')

                    # Remove case named "Name"
                    df = df.drop("Name", axis=1)

                    # Graph creation
                    G = nx.Graph()

                    for node in df.columns:
                        node_layer = nm.get_layer(node)  # Retrieve the layer for the node
                        G.add_node(node, layer=nm.get_layer(node))
                        if node_layer not in layer_colors:
                            print(f"Warning: No color assigned for layer {node_layer}. Defaulting to grey.")


                    ### Adding edges based on correlation values
                    ### Use a different threshold for interlayer edges and intralayer edges
                                    # # Negative interval : 
                    min_neg_tresh = -1
                    max_neg_tresh = -treshold       # p<0.05 : left : 0.128  #right : 0.154         p<0.01 : left : 0.168  # right : 0.199
                    # Positive interval :                               # 0.192 tests   0.19 tracts
                    min_pos__tresh = treshold                # pour 126 patients       p<0.05 : 0.175                p<0.01 : 0.229
                    max_pos__tresh = 1

                    for j, node1 in enumerate(df.columns):
                        for k, node2 in enumerate(df.columns):
                            if j < k:  # To avoid duplicates
                                weight = df.iloc[j, k]
                                # Separate the three different edges to be able to each define an interval
                                                    # Separate the three different edges to be able to each define an interval
                                if (min_neg_tresh <= weight <= max_neg_tresh or min_pos__tresh <= weight <= max_pos__tresh):
                                        G.add_edge(node1, node2, weight=weight)

                    label = nm.get_label(layers)
                    #nodes = get_nodes_from_layers(G,layers)

                    # PLOT : Creating a 3D figure
                    #pos_xy = nx.spring_layout(G, k=10)

                    #pos_xy = nx.circular_layout(G)

                    layer_positions = {}
                    for layer in layers:
                        nodes_in_layer = [n for n in G.nodes if G.nodes[n]['layer'] == layer]
                        scales = {1: 2, 2: 3, 3: 1}  # Rayon différent pour chaque couche
                        circular_pos = nx.circular_layout(G.subgraph(nodes_in_layer), scale=scales[layer])
                        z = get_z_pos(layer)  # Assign the correct Z coordinate
                        for node, (x, y) in circular_pos.items():
                            layer_positions[node] = (x, y, z)  # Store 3D positions

                    pos_xy = layer_positions


                    #pos_xy = nx.shell_layout(G)
                    #pos_xy = nx.spectral_layout(G)
                    #pos_xy = nx.kamada_kawai_layout(G)
                    #pos_xy = nx.multipartite_layout(G, subset_key="layer", scale=50)

                    #pos_xy = nx.spring_layout(G, k=3)
                    fig = plt.figure(figsize=(10, 8))
                    ax = fig.add_subplot(111, projection='3d')

                    # Set axis labels
                    ax.set_xlabel('X Axis')
                    ax.set_ylabel('Y Axis')
                    ax.set_zlabel('Layer')

                    # Remove graduations (ticks)
                    ax.set_xticks([])  # From X axis
                    ax.set_yticks([])  # From y axis
                    ax.set_zticks([])  # From z axis

                    ax.view_init(elev=20, azim=30)  # Change l'angle de vue

                    ## Set title
                    #plt.title(rf"Correlation_plot_{label}_{hemi}_{imp}")

                    # Dictionary for storing associations between node numbers and names
                    node_label_mapping = {node: idx+1 for idx, node in enumerate(G.nodes())}

                    # Creating a legend with the names of the nodes and their associated number
                    legend_elements = []

                    for node in G.nodes():
                        node_num = node_label_mapping[node]  # The number assigned to the node
                        node_color = layer_colors.get(G.nodes[node]['layer'], 'grey') # Get the color specific to the node in the graph
                        legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor=node_color, markersize=10, label=f"{node_num}: {node}"))

                    # Get nodes z position
                    pos = {node: (pos_xy.get(node)[0], pos_xy.get(node)[1], get_z_pos(G.nodes[node]['layer'])) for node in G.nodes()}
                    # Draw a plane for each layer
                    layer_z_pos = [get_z_pos(i) for i in layers]
                    draw_planes(pos, layer_z_pos, ax)
                    # Plot nodes
                    for node, (x, y, z) in pos.items():
                        # Retrieve the correct color for each node's layer from layer_colors
                        node_color = layer_colors.get(G.nodes[node]['layer'], 'grey')
                        ax.scatter(x, y, z, color=node_color, s=60, zorder=2, edgecolors='black')
                        ax.text(x, y, z, str(node_label_mapping[node]), fontsize=8, color="black", fontweight = "bold", zorder=70)

                    # Drawing edges
                    for edge in G.edges():
                        x = np.array((pos[edge[0]][0], pos[edge[1]][0]))
                        y = np.array((pos[edge[0]][1], pos[edge[1]][1]))
                        z = np.array((pos[edge[0]][2], pos[edge[1]][2]))
                        weight = G.edges[edge]['weight']
                        # Normalizing weights :
                        #normalized_weight = max(0.5, min(5, abs(weight) * 2))  # Adjuste 10 factor if you want
                        # Check if edges connect nodes from different layers
                        # if G.nodes[edge[0]]['layer'] != G.nodes[edge[1]]['layer']:
                        #     linestyle = '--'   # Use the dashed line style for inter-layer edges (type, (taille))
                        # else:
                        #     linestyle = 'solid'   # Use solid line style for intra-layer edges

                        if weight < 0:
                            linestyle = '--'
                        else : 
                            linestyle = 'solid'       

                        # # Color negative correlations in red and positive ones in black
                        # if weight < 0:
                        #     edge_color = "red"
                        # else : 
                        #     edge_color = "green"   

                        ax.plot(x, y, z, color='grey', linestyle=linestyle, linewidth = 0.5)      #linewidth = normalized_weight

                        
                ax.set_axis_off()

                # Create a new figure for the legend
                legend_fig = plt.figure(figsize=(4, 6))  # Adjust size as needed
                ax_legend = legend_fig.add_subplot(111)

                # Create a legend with two columns
                ax_legend.legend(handles=legend_elements, loc='center', title="Node Legend", ncol=2)    #bbox_to_anchor=(1, 0.5)

                # Remove axes from the legend figure
                ax_legend.axis('off')
                

                # Save multilayers plots
                save_multilayers_plots(fig, legend_fig, hemi, imp, label, treshold)

                # # # Display graph
                # plt.show() 

if __name__ == '__main__':
    main()
