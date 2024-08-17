import numpy as np
from data_loader_npy import DataLoader
from data_analyze.ANOVA_data import ANOVADATA
from data_analyze.PCA_data import PCADATA
from data_analyze.T_TEST_data import TTESTDATA
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import matplotlib.pyplot as plt

'''

***Interpreting the Results:
PCA: Look at the explained variance to decide how many principal components to keep. Components with low variance may be excluded.
ANOVA: Features with high F-values and low p-values (below 0.05) are considered important.
T-Test: Features with high absolute T-values and low p-values are significant.

***Feature Selection:
Based on the results from PCA, ANOVA, and T-Test:

PCA: You may choose to reduce dimensionality by selecting a subset of principal components.
ANOVA/T-Test: Features with low p-values should be kept, while those with high p-values could be candidates for removal.

***Summary:
PCA: Reduces dimensionality and visualizes the variance explained by each component.
ANOVA: Checks the statistical significance of each feature.
T-Test: Compares feature importance between two groups.
Visualize: Plot the results using Matplotlib to help decide on feature selection.

'''
if __name__ == '__main__':

    box_path = r'CNN_Regression\data\training_data\set.000\box.npy'
    energy_path = r'CNN_Regression\data\training_data\set.000\energy.npy'
    coord_path = r'CNN_Regression\data\training_data\set.000\coord.npy'

    box_features = DataLoader(box_path)
    coord_features  = DataLoader(coord_path)
    eneryg_target = DataLoader(energy_path)

    X1 = box_features.prepare_data()
    X2 = coord_features.prepare_data()
    y = eneryg_target.prepare_data()

    X_combined = np.concatenate((X1, X2), axis=1)  # Shape: (161, 24)


    X_combined = X_combined.reshape((X_combined.shape[0], X_combined.shape[1], 1))  # Shape: (161, 24, 1)
    X_combined_2D = X_combined.reshape(X_combined.shape[0], X_combined.shape[1])

    # Check for NaN or infinite values in your data
    if np.any(np.isnan(X_combined_2D)) or np.any(np.isinf(X_combined_2D)) or np.any(np.isnan(y)) or np.any(np.isinf(y)) :
        exit(-1)


    # Standardize the features
    scaler = StandardScaler()
    X_combined_standardized = scaler.fit_transform(X_combined_2D)
    # Plot histograms of the features
    plt.figure(figsize=(15, 10))
    for i in range(X_combined_standardized.shape[1]):
        plt.subplot(4, 6, i+1)
        sns.histplot(X_combined_standardized[:, i], kde=True)
        plt.title(f'Feature {i+1}')
    plt.tight_layout()
    plt.show()
    
    PCADATA(X_combined_standardized, y)
    # ANOVADATA(X_combined_standardized, y)
    # TTESTDATA(X_combined_standardized, y)

