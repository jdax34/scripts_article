from my_globals import *
import pandas as pd
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import numpy as np

# Initialize variable lists
test_name = ["LB", "BELLS", "CODES", "DO80", "DS_F", "DS_B", "FIG_C", "FIG_R", "FLU_A", "FLU_P", "PPTT", "RLRI_E", "RLRI_FR", "RLRI_TR", "STROOP_D", "STROOP_R", "STROOP_ID", "TMT_A", "TMT_BA"]
hemisphere = ["L", "R"]
longitude = ["Pre", "Post_3M"]
imp = [1, 2, 3, 4, 5]

# Loop through all combinations of test names, hemispheres, time points, and imputations
for test in test_name:
    for hemi in hemisphere:
        for longit in longitude:
            for i in imp:
                X_data = []
                y_data = []
                

                # For deficit percentage data
                file_path = rf"{MAIN_PATH}\Données\TESTS\2_DEFICIT_PERCENTAGE_DATA\{hemi}_DEFICIT_PERCENTAGE_DATA\{test}\Deficit_Percentage_{test}_{i}.csv"

                # Check if the file exists
                if not os.path.exists(file_path):
                    print(f"File does not exist for {test}, {hemi}, {i}.")
                else:
                    # Load the data into a DataFrame
                    df = pd.read_csv(file_path, delimiter=';')

                    # Define predictors (AGE and NSE) and target variable (test score)
                    X_data = df[['AGE', 'NSE']]
                    y_data = df[f"{test}"]

                    # Create and fit the linear regression model
                    model = LinearRegression()
                    model.fit(X_data, y_data)

                    # Predict the target variable
                    y_pred = model.predict(X_data)

                    # Compute residuals (difference between actual and predicted values)
                    residuals = y_data - y_pred

                    # Normalize the residuals using StandardScaler
                    scaler = StandardScaler()
                    residuals_array = np.array(residuals)  # Convert to NumPy array
                    residuals_normalized = scaler.fit_transform(residuals_array.reshape(-1, 1))

                    # Store the normalized residuals in a DataFrame
                    residuals_df = pd.DataFrame({rf'{test}_{hemi}': residuals_normalized.squeeze()})

                    # Define the destination directory and file path
                    dir = rf"{MAIN_PATH}\Données\TESTS\3_REG_MUL_DATA\{hemi}_REG_DATA\{test}"
                    path_destination = dir + rf"\Reg_Lin_{test}_{i}.csv"

                    # Create the destination directory if it doesn't exist
                    os.makedirs(dir, exist_ok=True)

                    # Save the residuals to a CSV file
                    residuals_df.to_csv(path_destination, sep=';', index=False)

                    # Optional: print confirmation message
                    # print("Normalized residuals saved successfully.")
