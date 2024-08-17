from scipy.stats import ttest_ind
import numpy as np
import matplotlib.pyplot as plt


class TTESTDATA():
    def __init__(self, X_combined_standardized, y) -> None:

        # Example: T-Test between high-energy and low-energy groups

        high_energy = X_combined_standardized[y > np.median(y)]
        low_energy = X_combined_standardized[y <= np.median(y)]

        t_values, p_values_ttest = ttest_ind(high_energy, low_energy, nan_policy='omit')

        # Plot T-values and p-values
        plt.figure(figsize=(10, 6))
        plt.bar(range(X_combined_standardized.shape[1]), np.abs(t_values), alpha=0.5, align='center')
        plt.xlabel('Feature Index')
        plt.ylabel('T-value')
        plt.title('T-Test T-value for Each Feature')
        plt.grid(True)
        plt.show()

        plt.figure(figsize=(10, 6))
        plt.bar(range(X_combined_standardized.shape[1]), p_values_ttest, alpha=0.5, align='center')
        plt.xlabel('Feature Index')
        plt.ylabel('p-value')
        plt.title('T-Test p-value for Each Feature')
        plt.axhline(y=0.05, color='r', linestyle='--', label='0.05 significance level')
        plt.legend()
        plt.grid(True)
        plt.show()
