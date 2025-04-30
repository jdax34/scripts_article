from my_globals import *
import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import StandardScaler

# Define test categories based on how performance is interpreted
test_name = ["CODES", "DO80", "DS_F", "DS_B", "FIG_C", "FIG_R", "FLU_A", "FLU_P", "PPTT", "RLRI_E", "RLRI_FR", "RLRI_TR"]  # Higher score = better performance
test_name_inv = ["STROOP_D", "STROOP_R", "STROOP_ID", "TMT_A", "TMT_BA"]  # Higher score = worse performance
test_name_biss = ["LB"]  # Lateralized test: deficit = deviation toward the left
test_name_cloches = ["BELLS"]  # Lateralized test: deficit = deviation toward the left (non-inverted)

# Define hemispheres and imputations
hemisphere = ["L", "R"]
imp = [1, 2, 3, 4, 5]

# Process tests where a higher score indicates better performance
for test in test_name:
    for hemi in hemisphere:
        for i in imp:
            file_path = rf"{MAIN_PATH}\Données\TESTS\1_GROUPING_PRE_POST\PRE_POST_{hemi}\{test}\Pre_Post_{test}_{i}.csv"

            # Check file existence
            if not os.path.exists(file_path):
                print(f"File does not exist for {test}, {hemi}, {i}.")
            else:
                # Load the data
                df = pd.read_csv(file_path, delimiter=';')

                # Calculate percentage of performance decrease (deficit)
                df[f'{test}'] = (-(df[f'{test}_Post_3M'] - df[f'{test}_Pre']) / df[f'{test}_Pre']) * 100

                # Round values
                df = df.round(3)

                # Create output directory and save new file
                dir = rf"{MAIN_PATH}\Données\TESTS\2_DEFICIT_PERCENTAGE_DATA\{hemi}_DEFICIT_PERCENTAGE_DATA\{test}"
                path_destination = dir + rf"\Deficit_Percentage_{test}_{i}.csv"
                os.makedirs(dir, exist_ok=True)
                df.to_csv(path_destination, sep=';', index=False)

# Process tests where a higher score indicates worse performance
for test in test_name_inv:
    for hemi in hemisphere:
        for i in imp:
            file_path = rf"{MAIN_PATH}\Données\TESTS\1_GROUPING_PRE_POST\PRE_POST_{hemi}\{test}\Pre_Post_{test}_{i}.csv"

            # Check file existence
            if not os.path.exists(file_path):
                print(f"File does not exist for {test}, {hemi}, {i}.")
            else:
                # Load the data
                df = pd.read_csv(file_path, delimiter=';')

                # Calculate percentage of performance increase (deficit)
                df[f'{test}'] = ((df[f'{test}_Post_3M'] - df[f'{test}_Pre']) / df[f'{test}_Pre']) * 100

                # Round values
                df = df.round(3)

                # Create output directory and save new file
                dir = rf"{MAIN_PATH}\Données\TESTS\2_DEFICIT_PERCENTAGE_DATA\{hemi}_DEFICIT_PERCENTAGE_DATA\{test}"
                path_destination = dir + rf"\Deficit_Percentage_{test}_{i}.csv"
                os.makedirs(dir, exist_ok=True)
                df.to_csv(path_destination, sep=';', index=False)

# Process "LB" test: directional score (left bias)
for test in test_name_biss:
    for hemi in hemisphere:
        for i in imp:
            file_path = rf"{MAIN_PATH}\Données\TESTS\1_GROUPING_PRE_POST\PRE_POST_{hemi}\{test}\Pre_Post_{test}_{i}.csv"

            # Check file existence
            if not os.path.exists(file_path):
                print(f"File does not exist for {test}, {hemi}, {i}.")
            else:
                # Load the data
                df = pd.read_csv(file_path, delimiter=';')

                # Compute directional difference (deficit toward the left is positive)
                df[f'{test}'] = -(df[f'{test}_Pre'] - df[f'{test}_Post_3M'])

                # Round values
                df = df.round(3)

                # Create output directory and save new file
                dir = rf"{MAIN_PATH}\Données\TESTS\2_DEFICIT_PERCENTAGE_DATA\{hemi}_DEFICIT_PERCENTAGE_DATA\{test}"
                path_destination = dir + rf"\Deficit_Percentage_{test}_{i}.csv"
                os.makedirs(dir, exist_ok=True)
                df.to_csv(path_destination, sep=';', index=False)

# Process "BELLS" test: directional score (deficit = more leftward deviation)
for test in test_name_cloches:
    for hemi in hemisphere:
        for i in imp:
            file_path = rf"{MAIN_PATH}\Données\TESTS\1_GROUPING_PRE_POST\PRE_POST_{hemi}\{test}\Pre_Post_{test}_{i}.csv"

            # Check file existence
            if not os.path.exists(file_path):
                print(f"File does not exist for {test}, {hemi}, {i}.")
            else:
                # Load the data
                df = pd.read_csv(file_path, delimiter=';')

                # Compute directional difference (deficit toward the left is positive)
                df[f'{test}'] = (df[f'{test}_Post_3M'] - df[f'{test}_Pre'])

                # Round values
                df = df.round(3)

                # Create output directory and save new file
                dir = rf"{MAIN_PATH}\Données\TESTS\2_DEFICIT_PERCENTAGE_DATA\{hemi}_DEFICIT_PERCENTAGE_DATA\{test}"
                path_destination = dir + rf"\Deficit_Percentage_{test}_{i}.csv"
                os.makedirs(dir, exist_ok=True)
                df.to_csv(path_destination, sep=';', index=False)
