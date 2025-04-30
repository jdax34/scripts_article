from my_globals import *
import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import StandardScaler

# List of cognitive test names
test_name = ["LB", "BELLS", "CODES", "DO80", "DS_F", "DS_B", "FIG_C", "FIG_R", 
             "FLU_A", "FLU_P", "PPTT", "RLRI_E", "RLRI_FR", "RLRI_TR", 
             "STROOP_D", "STROOP_R", "STROOP_ID", "TMT_A", "TMT_BA"]

# Hemispheres
hemisphere = ["L", "R"]

# List of imputation indexes
imp = [1, 2, 3, 4, 5]

# Loop through all combinations of test, hemisphere, and imputation index
for test in test_name:
    for hemi in hemisphere:
        for i in imp:
            # Define the file paths for the Pre and Post_3M imputation files
            file_path_1 = rf"{MAIN_PATH}\Données\TESTS\0_AFTER_IMPUTATIONS\pmm\{hemi}\{test}\Pre\IMPUTATION_{test}_{i}.csv"
            file_path_2 = rf"{MAIN_PATH}\Données\TESTS\0_AFTER_IMPUTATIONS\pmm\{hemi}\{test}\Post_3M\IMPUTATION_{test}_{i}.csv"

            # Check if the Pre file exists
            if not os.path.exists(file_path_1):
                print(f"File does not exist for {test}, {hemi}, {i}.")
            else:
                # Read the Pre file into a DataFrame
                df_Pre = pd.read_csv(file_path_1, delimiter=';')

            # Check if the Post_3M file exists
            if not os.path.exists(file_path_2):
                print(f"File does not exist for {test}, {hemi}, {i}.")
            else:
                # Read the Post_3M file into a DataFrame
                df_Post_3M = pd.read_csv(file_path_2, delimiter=';')

                # Extract the fourth column from the Post_3M DataFrame
                col_to_add = df_Post_3M.iloc[:, 3]

                # Add the extracted column to the Pre DataFrame
                df_Pre[f'{test}_Post_3M'] = col_to_add

                # Define the output directory and file path
                dir = rf"{MAIN_PATH}\Données\TESTS\1_GROUPING_PRE_POST\PRE_POST_{hemi}\{test}"
                path_destination = dir + rf"\Pre_Post_{test}_{i}.csv"
                os.makedirs(dir, exist_ok=True)

                # Save the updated DataFrame to the new CSV file
                df_Pre.to_csv(path_destination, sep=';', index=False)
