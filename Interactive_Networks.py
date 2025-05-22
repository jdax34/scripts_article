from my_globals import *
import pandas as pd
import networkx as nx
import os
from pyvis.network import Network
from IPython.display import IFrame
import network_manipulation as nm

# Function to determine file path based on selected layers, hemisphere, and imputation
def get_path(layers, hemi, imp):
    if layers == [1,2,3]:
        return rf"{MAIN_PATH}\Coding\Correlation_Matrix\DECO_TESTS_DAMAGE\Spearman_Corr_Matrix_{hemi}_{imp}.csv"
    elif layers == [1,2]: 
        return rf"{MAIN_PATH}\Coding\Correlation_Matrix\DECO_AND_TESTS\Spearman_Corr_Matrix_{hemi}_{imp}.csv"
    elif layers == [1,3]: 
        return rf"{MAIN_PATH}\Coding\Correlation_Matrix\TESTS_AND_DAMAGE\Spearman_Corr_Matrix_{hemi}_{imp}.csv"
    elif layers == [2,3]: 
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

# Main script entry point
if __name__ == '__main__':

    layers = [1]  # Define which layers to analyze: [1]=NT, [2]=SD, [3]=CD, [1,2], [1,3], [2,3], [1,2,3]
    hemis = ['L', 'R']  # Hemispheres: Left and Right
    imps = ['1', '2', '3', '4', '5', 'mean']  # Imputation strategies
    network_analyses = ["betweenness_centrality", "closeness_centrality", "degree_centrality", "clustering_coefficient"]
    label = nm.get_label(layers)  # Get the appropriate label for the combination of layers
    tresholds = [0.175, 0.229]  # Thresholds for correlation filtering (e.g., p<0.05, p<0.01)

    for network_analysis in network_analyses:
        for treshold in tresholds:
            for hemi in hemis:
                for imp in imps:
                    # Load the corresponding correlation matrix file
                    file_path = get_path(layers, hemi, imp)

                    if not os.path.exists(file_path):
                        print(f"File does not exist for hemisphere {hemi}, imputation {imp}.")
                    else:
                        df = pd.read_csv(file_path, delimiter=';')
                        df = df.drop("Name", axis=1)  # Remove identifier column

                        # Create empty NetworkX graphs
                        G = nx.Graph()
                        G_analyses = nx.Graph()

                        # Define colors for each layer
                        layer_colors = {
                            1: '#00008d',  # Blue: neuropsychological scores
                            2: '#006300',  # Green: subcortical damage
                            3: '#fb0000'   # Red: cortical damage
                        }

                    # Choose appropriate network analysis file path
                    if layers in [[2], [2, 3], [3]]:
                        file_path_analyses = rf"{MAIN_PATH}\Coding\Networks_Analyses\Analyses\{treshold}\{network_analysis}\{hemi}\{label}\{label}_{network_analysis}_{hemi}.csv"
                    else:
                        file_path_analyses = rf"{MAIN_PATH}\Coding\Networks_Analyses\Analyses\{treshold}\{network_analysis}\{hemi}\{label}\{label}_{network_analysis}_{hemi}_{imp}.csv"

                    if not os.path.exists(file_path_analyses):
                        print(f"Analysis file does not exist for hemisphere {hemi}, imputation {imp}.")
                    else:
                        net_analyses_df = pd.read_csv(file_path_analyses, delimiter=';')
                        # Map node sizes from centrality values
                        node_sizes = {
                            row[net_analyses_df.columns[0]]: row[net_analyses_df.columns[1]]
                            for idx, row in net_analyses_df.iterrows()
                        }

                        # Add nodes to both graphs
                        for node in df.columns[1:]:
                            layer = nm.get_layer(node)
                            color = layer_colors.get(layer)
                            size = node_sizes.get(node, 10) * 100  # Scale centrality for visualization
                            G.add_node(node, label=str(node), color=color, opacity=0.2)
                            G_analyses.add_node(node, label=str(node), color=color, opacity=0.2, size=size)

                        # Define thresholds for filtering edges
                        min_pos__tresh = treshold
                        max_pos__tresh = 1

                        # Add edges based on correlation strength
                        for j, node1 in enumerate(df.columns[1:]):
                            for k, node2 in enumerate(df.columns[1:]):
                                if j < k:
                                    weight = df.iloc[j+1, k+1]
                                    if min_pos__tresh <= weight <= max_pos__tresh:
                                        G.add_edge(node1, node2, weight=weight*10)
                                        G_analyses.add_edge(node1, node2, weight=weight*10)

                        # Create Pyvis visualizations
                        net = Network(notebook=True, cdn_resources='in_line')
                        net.from_nx(G, show_edge_weights=True)

                        net_analyses = Network(notebook=True, cdn_resources='in_line')
                        net_analyses.from_nx(G_analyses, show_edge_weights=True)

                        # Set node and edge appearance
                        net.set_options("""
                        {
                            "nodes": {
                                "color": {"inherit": true},
                                "font": {"face": "Tahoma"}
                            },
                            "edges": {
                                "color": {
                                    "inherit": true,
                                    "color": "rgba(211,211,211,0.5)",
                                    "highlight": "black",
                                    "hover": "black"
                                },
                                "hoverWidth": 1,
                                "smooth": false
                            }
                        }
                        """)

                        net_analyses.set_options("""
                        var options = {
                            "nodes": {
                                "opacity": 0.2,
                                "scaling": {"min": 10, "max": 30},
                                "color": {
                                    "inherit": true,
                                    "color": "rgba(0,0,0,0.2)",
                                    "highlight": "black",
                                    "hover": "black"
                                },
                                "font": {"face": "Tahoma"}
                            },
                            "edges": {
                                "color": {
                                    "inherit": true,
                                    "color": "rgba(0,0,0,0.2)",
                                    "highlight": "black",
                                    "hover": "black"
                                },
                                "opacity": 0.2,
                                "smooth": {"enabled": false, "type": "dynamic"}
                            },
                            "interaction": {
                                "hover": false,
                                "tooltipDelay": 200,
                                "hideEdgesOnDrag": false,
                                "hideNodesOnDrag": false
                            },
                            "physics": {
                                "barnesHut": {
                                    "gravitationalConstant": -20000,
                                    "centralGravity": 0.3,
                                    "springLength": 250,
                                    "springConstant": 0.04,
                                    "damping": 0.09
                                },
                                "minVelocity": 0.0,
                                "solver": "barnesHut"
                            }
                        }
                        """)

                        # Generate HTML visualizations
                        html_content = net.generate_html()
                        html_content_analyses = net_analyses.generate_html()

                        # Create output directories
                        output_dir = os.path.join(MAIN_PATH_WIN, f"Coding/Correlation_Matrix/Interactive_Plots/{treshold}/{hemi}/{label}")
                        output_dir_analyses = os.path.join(MAIN_PATH_WIN, f"Coding/Networks_Analyses/Analyses/{treshold}/{network_analysis}/{hemi}/{label}/")

                        os.makedirs(output_dir, exist_ok=True)
                        os.makedirs(output_dir_analyses, exist_ok=True)

                        # Define destination file paths
                        file_path_destination = os.path.join(output_dir, f"interactiveplot_{label}_{hemi}_{imp}.html")

                        if layers in [[2], [2, 3], [3]]:
                            file_path_analyses_destination = os.path.join(output_dir_analyses, f"interactiveplot_{label}_{network_analysis}_{hemi}.html")
                        else:
                            file_path_analyses_destination = os.path.join(output_dir_analyses, f"interactiveplot_{label}_{network_analysis}_{hemi}_{imp}.html")

                        # Add an HTML legend to the visualizations 
                        legend_html = f"""
                        <div style="position: absolute; top: 10px; right: 10px; background: white; padding: 10px; border: 1px solid #ccc; font-family: Tahoma; font-size: 14px; z-index: 999;">
                        <strong>Légende</strong><br>
                        <span style="color:#00008d;">■</span> NT<br>
                        <span style="color:#006300;">■</span> SD<br>
                        <span style="color:#fb0000;">■</span> CD<br>
                        """

                        # Inject legend
                        html_content += legend_html
                        html_content_analyses += legend_html
                        
                        # Write HTML files to disk
                        with open(file_path_destination, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        with open(file_path_analyses_destination, 'w', encoding='utf-8') as f:
                            f.write(html_content_analyses)
