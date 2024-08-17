from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class PCADATA():
    def __init__(self, X_combined_standardized, y):
        feature_names = None
        if feature_names is None:
            feature_names = [f'feature{i+1}' for i in range(X_combined_standardized.shape[1])]
        elif len(feature_names) != X_combined_standardized.shape[1]:
            raise ValueError(f"feature_names length {len(feature_names)} does not match number of features {X_combined_standardized.shape[1]}")

        # Run PCA
        pca = PCA(n_components=0.95)  # Keep 95% of variance
        X_pca = pca.fit_transform(X_combined_standardized)
        
        # Explained variance plot with feature labels
        plt.figure(figsize=(10, 6))
        plt.plot(np.cumsum(pca.explained_variance_ratio_), marker='o')
        plt.xlabel('Number of Components')
        plt.ylabel('Cumulative Explained Variance')
        plt.title('PCA Explained Variance')
        for i, ratio in enumerate(np.cumsum(pca.explained_variance_ratio_)):
            plt.text(i, ratio, f'PC{i+1}', fontsize=12)
        plt.grid(True)
        plt.show()

        # Bar plot of explained variance by each component with labels
        plt.figure(figsize=(10, 6))
        plt.bar(range(1, len(pca.explained_variance_ratio_) + 1), pca.explained_variance_ratio_, alpha=0.5, align='center')
        plt.xlabel('Principal Components')
        plt.ylabel('Explained Variance')
        plt.title('Explained Variance by Each Principal Component')
        plt.grid(True)
        plt.show()

        # Visualize the first two principal components
        plt.figure(figsize=(10, 6))
        plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap='viridis', edgecolor='k', s=50)
        plt.xlabel('First Principal Component')
        plt.ylabel('Second Principal Component')
        plt.title('PCA - First Two Principal Components')
        plt.colorbar(label='Energy Output')
        plt.grid(True)
        plt.show()

        # # Plot feature loadings for the first two principal components
        # if feature_names is not None:
        #     if len(feature_names) != X_combined_standardized.shape[1]:
        #         raise ValueError(f"feature_names length {len(feature_names)} does not match number of features {X_combined_standardized.shape[1]}")

        #     loadings = pd.DataFrame(pca.components_.T, columns=[f'PC{i+1}' for i in range(pca.components_.shape[0])], index=feature_names)

        #     plt.figure(figsize=(14, 8))
        #     plt.barh(loadings.index, loadings['PC1'], alpha=0.5, label='PC1')
        #     plt.barh(loadings.index, loadings['PC2'], alpha=0.5, label='PC2', color='orange')
        #     plt.xlabel('Feature Loadings')
        #     plt.ylabel('Original Features')
        #     plt.title('Feature Loadings for the First Two Principal Components')
        #     plt.legend()
        #     plt.grid(True)
        #     plt.show()

        # Loadings (feature contributions) for each principal component
        loadings = pd.DataFrame(pca.components_.T, columns=[f'PC{i+1}' for i in range(X_pca.shape[1])], index=feature_names)
        print("Loadings (contribution of original features to each PC):\n", loadings)

        # Identify the original features contributing the most to the components that explain 95% variance
        explained_variance_ratio = pca.explained_variance_ratio_
        significant_pcs = np.cumsum(explained_variance_ratio) <= 0.95  # Boolean mask to select significant PCs
        significant_loadings = loadings.loc[:, significant_pcs]

        # For each significant principal component, find the original features with the highest absolute loadings
        top_features = {}
        for pc in significant_loadings.columns:
            top_features[pc] = significant_loadings[pc].abs().nlargest(4).index.tolist()

        print("Top contributing original features for significant PCs:")
        for pc, features in top_features.items():
            print(f"{pc}: {features}")

        # Plot the feature loadings for the significant principal components
        plt.figure(figsize=(14, 8))
        for pc in significant_loadings.columns:
            plt.barh(loadings.index, significant_loadings[pc], alpha=0.5, label=pc)
        plt.xlabel('Feature Loadings')
        plt.ylabel('Original Features')
        plt.title('Feature Loadings for Significant Principal Components')
        plt.legend()
        plt.grid(True)
        plt.show()
# Example usage:
# feature_names = ['feature1', 'feature2', ..., 'featureN']
# pca_data = PCADATA(X_combined_standardized, y, feature_names)



