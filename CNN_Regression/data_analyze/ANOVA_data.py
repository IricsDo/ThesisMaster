from sklearn.feature_selection import f_classif, f_regression
import matplotlib.pyplot as plt

class ANOVADATA():
    def __init__(self, X_combined_standardized, y) -> None:
        # Perform ANOVA F-test (for regression problems use f_regression)

        f_values, p_values = f_regression(X_combined_standardized, y)

        # Plot F-values and p-values
        plt.figure(figsize=(10, 6))
        plt.bar(range(X_combined_standardized.shape[1]), f_values, alpha=0.5, align='center')
        plt.xlabel('Feature Index')
        plt.ylabel('F-value')
        plt.title('ANOVA F-value for Each Feature')
        plt.grid(True)
        plt.show()

        plt.figure(figsize=(10, 6))
        plt.bar(range(X_combined_standardized.shape[1]), p_values, alpha=0.5, align='center')
        plt.xlabel('Feature Index')
        plt.ylabel('p-value')
        plt.title('ANOVA p-value for Each Feature')
        plt.axhline(y=0.05, color='r', linestyle='--', label='0.05 significance level')
        plt.legend()
        plt.grid(True)
        plt.show()

