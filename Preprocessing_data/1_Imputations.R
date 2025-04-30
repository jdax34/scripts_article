# Load required libraries
library(broom)
library(broom.mixed)
library(ggplot2)
library(mice)
library(miceadds)
library(multilevel)
library(openxlsx)
library(pan)
library(readxl)
library(SparseM)
library(VIM)
library(dplyr)

#-------------------------------------------------------
# Function to build a custom predictor matrix
#-------------------------------------------------------
buildPredictorMatrix <- function (data, predictorColumnIndexList, imputedColumnIndex) {
  predictorMatrix <- matrix(0, nrow = ncol(data), ncol = ncol(data))
  dimnames(predictorMatrix) <- list(colnames(data), colnames(data))
  for (i in predictorColumnIndexList) {
    predictorMatrix[imputedColumnIndex, i] <- 1
  }
  return(predictorMatrix)
}

#-------------------------------------------------------
# Main function to perform imputation
#-------------------------------------------------------
perform_imputation <- function(test_name, method, limits, it_num, hemi, longit) {
  
  # Select column index based on the timepoint
  if(longit == "Pre") {
    col_index = 4
  } else if (longit == "Post_3M") {
    col_index = 5
  } else {
    return("Error: Invalid longitudinal timepoint.")
  }
  
  # Load input file
  if (!file.exists(paste0("Initial_Files/MICE_", test_name, "_", hemi, ".xlsx"))) {
    return("File does not exist.")
  }
  table <- read_excel(paste0("Initial_Files/MICE_", test_name, "_", hemi, ".xlsx"))
  
  # Create output directory if it doesn't exist
  output_path <- paste0("./Results/", method, "/", hemi, "/", test_name, "/", longit, "/")
  if (!file.exists(output_path)) {
    dir.create(output_path, recursive = TRUE, showWarnings = FALSE)
  }

  # Replace empty strings with NA in the target column
  column_name_to_impute <- paste0(test_name, '_', longit)
  table[[column_name_to_impute]] <- replace(table[[column_name_to_impute]], table[[column_name_to_impute]] == '', NA)

  #-----------------------
  # INITIAL IMPUTATION SETUP
  #-----------------------
  var_imp  <- table[, col_index]  # Target variable
  var_pred <- table[, c(2:3, col_index)]  # Predictor variables
  
  # Define custom predictor matrix
  pred <- buildPredictorMatrix(table, c(2,3), col_index)
  imp <- mice(table, maxit = 0, predictorMatrix = pred, defaultMethod = method, seed = 2018)
  
  # Set imputation method
  meth <- imp$meth
  meth[c(1,5)] <- ""  # Don't impute ID or hemisphere
  meth[col_index] <- method

  # Squeeze imputed values within clinical limits
  post <- imp$post
  post[col_index] <- paste0("imp[[j]][, i] <- squeeze(imp[[j]][, i], c(", limits[[1]], ",", limits[[2]], "))")
  
  # Ensure longitudinal imputation order
  visSeq <- imp$visitSequence

  #-----------------------
  # PRE-IMPUTATION MODEL CHECK
  #-----------------------
  formula_str <- paste0(test_name, "_", longit, " ~ AGE + NSE")
  fit_1 <- with(imp, lm(as.formula(formula_str)))
  pool.fit_1 <- pool(fit_1)

  #-----------------------
  # RUN IMPUTATION
  #-----------------------
  imp <- mice(table,
              method = meth,
              post = post,
              predictorMatrix = pred,
              visitSequence = visSeq,
              maxit = it_num,
              m = 5,  # number of imputed datasets
              seed = 2018,
              printFlag = FALSE)
  
  #-----------------------
  # POST-IMPUTATION MODEL CHECK
  #-----------------------
  fit_2 <- with(imp, lm(as.formula(formula_str)))
  pool.fit_2 <- pool(fit_2)

  # Combine model summaries
  summary_1 <- as.data.frame(summary(pool.fit_1))
  summary_2 <- as.data.frame(summary(pool.fit_2))
  combined_summary <- rbind(summary_1, summary_2)

  #-----------------------
  # SAVE IMPUTED DATASETS
  #-----------------------
  for (i in 1:5) {
    completeData <- complete(imp, i)
    if (!is.data.frame(completeData)) {
      completeData <- as.data.frame(completeData)
    }

    df_modified <- completeData
    
    # Remove extra column(s) based on the timepoint
    if (longit == "Pre") {
      df_modified <- df_modified[, -ncol(df_modified)]
    } else if (longit == "Post_3M") {
      df_modified <- df_modified[, - (ncol(df_modified) - 1)]
    }

    # Save imputed dataset
    file_name_output <- paste0("IMPUTATION_", test_name, "_", i, ".csv")
    write.table(df_modified, file.path(output_path, file_name_output), sep = ";", row.names = FALSE)
  }

  # Save pooled model summary
  file_name_output <- paste0(test_name, "_POOLFIT.csv")
  write.table(combined_summary, file.path(output_path, file_name_output), sep = ";", row.names = FALSE)

  #-----------------------
  # VISUALIZE IMPUTATION QUALITY
  #-----------------------
  png(paste0(output_path, test_name, "_", hemi, "_", longit, "_IMP_VS_OBS.png"), width = 500, height = 500)
  print(stripplot(imp, as.formula(paste0(column_name_to_impute, " ~ .imp")), jitter = TRUE))
  dev.off()
  
  return("success")
}

#-------------------------------------------------------
# MAIN EXECUTION LOOP
#-------------------------------------------------------

# Set working directory
setwd("C:\\Users\\roxan\\Desktop\\These\\Imputations")

# Define test names and limits
test_names <- c("LB", "BELLS", "CODES", "DO80", "DS_F", "DS_B", "FIG_C", "FIG_R", "FLU_A", "FLU_P", 
                "PPTT", "RLRI_E", "RLRI_FR", "RLRI_TR", "STROOP_D", "STROOP_R", "STROOP_ID", 
                "TMT_A", "TMT_BA")

columns_and_limits <- list(
  LB = c(-7.6, 8.8), BELLS = c(0, 10), CODES = c(20, 111), DO80 = c(61, 80), DS_F = c(3, 9),
  DS_B = c(2, 8), FIG_R = c(9, 36), FIG_C = c(27, 36), FLU_A = c(5, 62), FLU_P = c(1, 54),
  PPTT = c(39, 52), RLRI_E = c(3, 16), RLRI_FR = c(8, 47), RLRI_TR = c(25, 48),
  STROOP_D = c(34, 167), STROOP_ID = c(14, 196), STROOP_R = c(27, 160),
  TMT_A = c(12, 163), TMT_BA = c(3, 242)
)

# Loop through each configuration and apply imputations
for (method in list("pmm", "norm")) {
  print(paste0("Method: ", method))
  for (hemisphere in list("L", "R")) {
    print(paste0("    Hemisphere: ", hemisphere))
    for (test_name in test_names) {
      print(paste0("        Test: ", test_name))
      for (longitud in list("Pre", "Post_3M")) {
        print(paste0("            Timepoint: ", longitud))
        result <- perform_imputation(test_name, method, columns_and_limits[[test_name]], 10, hemisphere, longitud)
      }
    }
  }
}
