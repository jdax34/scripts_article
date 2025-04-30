import pandas as pd
import os

# Function to generate the source and destination file paths based on input parameters
def get_file_path(type_of_network, which_layers, hemi, imp=None):
    base_source_path = r"D:\These\Données"  # Base directory for the raw data files
    base_dest_path = r"D:\These\Coding\Correlation_Matrix"  # Base directory for saving correlation matrices

    # Determine the folder based on network type and layers involved
    if type_of_network == "3_layers":
        folder = "DECO_TESTS_DAMAGE"
    elif type_of_network == "2_layers":
        if which_layers == "deco_and_tests":
            folder = "DECO_AND_TESTS"
        elif which_layers == "tests_and_damage":
            folder = "TESTS_AND_DAMAGE"
        elif which_layers == "deco_and_damage":
            folder = "DECO_AND_DAMAGE"
    elif type_of_network == "one_by_one_layer":
        if which_layers == "tests":
            folder = "TESTS"
        elif which_layers == "deco":
            folder = "DECO"
        elif which_layers == "damage":
            folder = "DAMAGE"

    # Construct source file path based on the folder and naming conventions
    if folder in ["DECO_AND_TESTS", "DECO_TESTS_DAMAGE", "TESTS_AND_DAMAGE"]:
        filename = f"{hemi}_data_{imp}_filtered_80.csv"
        source_path = os.path.join(base_source_path, folder, f"{hemi}_DATA", filename)
    elif folder == "DECO_AND_DAMAGE":
        filename = f"{hemi}_data_filtered_80.csv"
        source_path = os.path.join(base_source_path, folder, f"{hemi}_DATA", filename)
    elif folder == "DAMAGE":
        filename = f"{hemi}_Percent_Damage_filtered_80.csv"
        source_path = os.path.join(base_source_path, folder, filename)
    elif folder == "DECO":
        filename = f"{hemi}_D_Data_Synth_filtered_80.csv"
        source_path = os.path.join(base_source_path, folder, filename)
    elif folder == "TESTS":
        filename = f"Pre_Network_{imp}.csv"
        source_path = os.path.join(base_source_path, folder, "4_PRE_NETWORK_DATA", f"{hemi}_PRE_NET_DATA", filename)

    # Construct destination file path for saving the Spearman correlation matrix
    if which_layers in ["deco_and_damage", "deco", "damage"]:
        filename = f"Spearman_Corr_Matrix_{hemi}.csv"
    else:
        filename = f"Spearman_Corr_Matrix_{hemi}_{imp}.csv"
    dest_path = os.path.join(base_dest_path, folder, filename)

    return source_path, dest_path

# Main block to loop through all network types, layers, hemispheres, and imputations (if needed)
if __name__ == '__main__':
    hemis = ['L', 'R']  # List of hemispheres
    imps = [1, 2, 3, 4, 5]  # List of imputation indices

    type_of_networks = ["3_layers", "2_layers", "one_by_one_layer"]  # List of network types
    
    for type_of_network in type_of_networks:
        # Define corresponding layers based on the network type
        if type_of_network == "3_layers":
            which_layers = ["deco_tests_damage"]
        elif type_of_network == "2_layers":
            which_layers = ["deco_and_tests", "tests_and_damage", "deco_and_damage"]
        elif type_of_network == "one_by_one_layer":
            which_layers = ["tests", "deco", "damage"]
        else:
            print("Error: wrong type of network.")
        
        # Loop through each layer combination and hemisphere
        for layers in which_layers:
            for hemi in hemis:
                # For single-file layers (without imputations)
                if layers in ["deco_and_damage", "deco", "damage"]:
                    source_path, dest_path = get_file_path(type_of_network, layers, hemi)
                    print("type:" + type_of_network + ';layers:' + layers + ';hemi:' + hemi)
                    if not os.path.exists(source_path):
                        print(f"File does not exist: {source_path}")
                        continue

                    # Read the data, compute Spearman correlation matrix, and save it
                    df = pd.read_csv(source_path, delimiter=';')
                    matrix_corr = df.corr(method='spearman')
                    df_corr = pd.DataFrame(matrix_corr)
                    df_corr.insert(0, 'Name', df_corr.index)
                    df_corr = df_corr.round(3)
                    df_corr.to_csv(dest_path, sep=';', index=False)
                
                # For cases with multiple imputations
                else:
                    for imp in imps:
                        source_path, dest_path = get_file_path(type_of_network, layers, hemi, imp)
                        print("type:" + type_of_network + ';layers:' + layers + ';hemi:' + hemi + ";imp:" + str(imp))
                        if not os.path.exists(source_path):
                            print(f"File does not exist: {source_path}")
                            continue

                        # Read the data, compute Spearman correlation matrix, and save it
                        df = pd.read_csv(source_path, delimiter=';')
                        matrix_corr = df.corr(method='spearman')
                        df_corr = pd.DataFrame(matrix_corr)
                        df_corr.insert(0, 'Name', df_corr.index)
                        df_corr = df_corr.round(3)
                        df_corr.to_csv(dest_path, sep=';', index=False)
