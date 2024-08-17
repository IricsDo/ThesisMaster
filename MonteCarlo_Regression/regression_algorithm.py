from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, BayesianRidge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import SGDRegressor
from sklearn.kernel_ridge import KernelRidge
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split

import numpy as np

class RegressionModule():
    def __init__(self) -> None:
        self.X = None
        self.y = None  
        self.model = None

    def set_data(self, X, y) -> None:
        self.X = X
        self.y = y

    def __linear_regression(self) ->list:
        # Linear Regression is suitable for predicting continuous values, assuming a linear relationship between input and output.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __polynomial_regression(self, degree=2) ->list:
        # Polynomial Regression is suitable for data with a polynomial relationship between features and target.
        poly_features = PolynomialFeatures(degree=degree)
        X_poly = poly_features.fit_transform(self.X)
        X_train, X_test, y_train, y_test = train_test_split(X_poly, self.y, test_size=0.2, random_state=42)
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __ridge_regression(self, alpha=1.0) ->list:
        # Ridge Regression is suitable for data with multicollinearity; it adds a penalty for large coefficients.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model = Ridge(alpha=alpha)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __lasso_regression(self, alpha=1.0) ->list:
        # Lasso Regression is suitable for feature selection as it can shrink some coefficients to zero.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model = Lasso(alpha=alpha)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __elasticNet_regression(self, alpha=1.0, l1_ratio=0.5) ->list:
        # ElasticNet combines the penalties of Ridge and Lasso, suitable for data with multicollinearity and when feature selection is needed.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __decision_tree_based_regression(self) ->list:
        # Decision Tree Regression is suitable for capturing non-linear relationships in the data.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model = DecisionTreeRegressor()
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __support_vector_regression(self, C=1.0, epsilon=0.1) ->list:
        # Support Vector Regression is suitable for regression problems with non-linear relationships and high-dimensional space.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model = SVR(C=C, epsilon=epsilon)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __random_forest_regression(self, n_estimators=100) ->list:
        # Random Forest Regression is suitable for non-linear data, reduces overfitting by averaging multiple decision trees.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model = RandomForestRegressor(n_estimators=n_estimators)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __bayesian_linear_regression(self) ->list:
        # Bayesian Linear Regression is suitable for estimating uncertainty in predictions, especially with small datasets.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model = BayesianRidge()
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __quantile_regression(self) ->None:
        pass

    def __principal_components_regression(self, n_components=2) ->list:
        # Principal Component Regression reduces dimensionality by using principal components as predictors.
        pca = PCA(n_components=n_components)
        X_pca = pca.fit_transform(self.X)
        X_train, X_test, y_train, y_test = train_test_split(X_pca, self.y, test_size=0.2, random_state=42)
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __partial_least_squares_regression(self, n_components=2) -> list:
        # Partial Least Squares Regression is suitable for datasets with multicollinearity
        # and when predictors exceed observations.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        
        # Ensure y_train and y_test are 1-dimensional
        if len(y_train.shape) > 1:
            y_train = y_train.ravel()
        if len(y_test.shape) > 1:
            y_test = y_test.to_numpy().flatten()
        
        self.model = PLSRegression(n_components=n_components)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        
        return self.metrics_model(y_test, y_pred)


    def __gradient_boosting_regression(self, n_estimators=100) ->list:
        # Gradient Boosting Regression is suitable for capturing complex patterns in data by sequentially adding trees.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model = GradientBoostingRegressor(n_estimators=n_estimators)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __stochastic_gradient_descent_regression(self, max_iter=1000, tol=1e-3) ->list:
        # Stochastic Gradient Descent Regression is suitable for large datasets and is efficient with sparse data.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model = SGDRegressor(max_iter=max_iter, tol=tol)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __bayesian_ridge_regression(self) ->list:
        # Bayesian Ridge Regression is suitable for data with potential outliers and helps estimate the uncertainty of coefficients.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model = BayesianRidge()
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __catBoost_regressor(self) -> None:
        pass

    def __kernel_ridge_regression(self, alpha=1.0, kernel='linear') ->list:
        # Kernel Ridge Regression is suitable for non-linear data and can handle complex decision boundaries.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model = KernelRidge(alpha=alpha, kernel=kernel)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __xgBoost_regressor(self, n_estimators=100) ->list:
        # XGBoost Regressor is suitable for large datasets and handles missing data well, providing high predictive accuracy.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model = XGBRegressor(n_estimators=n_estimators)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def __lgbm_regressor(self, n_estimators=100) ->list:
        # LightGBM Regressor is suitable for large datasets and provides high accuracy and efficiency.
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model = LGBMRegressor(n_estimators=n_estimators)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        return self.metrics_model(y_test, y_pred)

    def run_regression(self, type: str) -> list:
        result = list()
        try:
            if type == 'LR':
                result = self.__linear_regression()
            elif type == 'PR':
                result = self.__polynomial_regression()
            elif type == 'RR':
                result = self.__ridge_regression()
            elif type == 'Lasso':
                result = self.__lasso_regression()
            elif type == 'EN':
                result = self.__elasticNet_regression()
            elif type == 'DTR':
                result = self.__decision_tree_based_regression()
            elif type == 'SVR':
                result = self.__support_vector_regression()
            elif type == 'RFR':
                result = self.__random_forest_regression()
            elif type == 'BLR':
                result = self.__bayesian_linear_regression()
            elif type == 'BRR':
                result = self.__bayesian_ridge_regression()
            elif type == 'PCR':
                result = self.__principal_components_regression()
            elif type == 'PLSR':
                result = self.__partial_least_squares_regression()
            elif type == 'GBR':
                result = self.__gradient_boosting_regression()
            elif type == 'SGD':
                result = self.__stochastic_gradient_descent_regression()
            elif type == 'KRR':
                result = self.__kernel_ridge_regression()
            elif type == 'XGB':
                result = self.__xgBoost_regressor()
            elif type == 'LGBM':
                result = self.__lgbm_regressor()
        except Exception as e:
            print(e)

        finally:
            self.infor_model()
        
        return result

    def metrics_model(self, y_test, y_pred) ->list:
        # Flatten the arrays to ensure they are 1-dimensional
        y_test = y_test.to_numpy().flatten()
        y_pred = y_pred.ravel()

        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = mse ** 0.5
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        print(f'Mean Squared Error (MSE): {mse}')
        print(f'R-squared (R² Score): {r2}')
        print(f'Mean Absolute Error (MAE): {mae}')
        print(f'Root Mean Squared Error (RMSE): {rmse}')
        print(f'Mean Absolute Percentage Error (MAPE): {mape:.2f}%')
        return mse, r2, mae, rmse, mape

    def infor_model(self) ->None:
        if not self.model:
            return 'Model empty'
        coefficients = self.model.coef_ if hasattr(self.model, 'coef_') else None
        intercept = self.model.intercept_ if hasattr(self.model, 'intercept_') else None
        if coefficients is not None:
            feature_names = self.X.columns
            print("Coefficients:")
            for feature, coef in zip(feature_names, coefficients):
                print(f"{feature}: {coef}")
        if intercept is not None:
            print(f"Intercept: {intercept}")
