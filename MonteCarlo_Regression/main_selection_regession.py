from regression_algorithm import RegressionModule
from lazypredict_algorithm import LazyRegressorModule
from MonteCarlo_Regression.data_loader_xlsx import DataLoader

if __name__ == '__main__':
    dl = DataLoader('H-Pt(100)_Eads.xlsx')
    X, y = dl.prepare_data()

    ra = RegressionModule()
    ra.set_data(X, y)

    while True:
        print("Select a regression algorithm to run:")
        print("1. Linear Regression (LR) - Suitable for small data")
        print("2. Polynomial Regression (PR) - Suitable for small data")
        print("3. Ridge Regression (RR) - Suitable for small data")
        print("4. Lasso Regression (Lasso) - Suitable for small data")
        print("5. ElasticNet Regression (EN) - Suitable for small data")
        print("6. Decision Tree Regression (DTR) - Suitable for small to large data")
        print("7. Support Vector Regression (SVR) - Suitable for small to medium data")
        print("8. Random Forest Regression (RFR) - Suitable for medium to large data")
        print("9. Bayesian Linear Regression (BLR) - Suitable for small data")
        print("10. Principal Components Regression (PCR) - Suitable for small to medium data")
        print("11. Partial Least Squares Regression (PLSR) - Suitable for small to medium data")
        print("12. Gradient Boosting Regression (GBR) - Suitable for medium to large data")
        print("13. Stochastic Gradient Descent Regression (SGD) - Suitable for large data")
        print("14. Bayesian Ridge Regression (BRR) - Suitable for small data")
        print("15. Kernel Ridge Regression (KRR) - Suitable for small to medium data")
        print("16. XGBoost Regressor (XGB) - Suitable for medium to large data")
        print("17. LightGBM Regressor (LGBM) - Suitable for medium to large data")
        print("18. Lazy Regressor (Lazy) - Automatically selects the best algorithm")
        print("0. Exit")


        choice = input("Enter the number corresponding to your choice: ")

        if choice == '0':
            break
        elif choice == '18':
            lr = LazyRegressorModule()
            lr.set_data(X, y)
            lr.run_lazy_regressor()
        else:
            try:
                choice = int(choice)
                algorithms = [
                    'LR', 'PR', 'RR', 'Lasso', 'EN', 'DTR', 'SVR', 'RFR',
                    'BLR', 'PCR', 'PLSR', 'GBR', 'SGD', 'BRR', 
                    'KRR', 'XGB', 'LGBM'
                ]
                if 1 <= choice <= len(algorithms):
                    ra.run_regression(algorithms[choice - 1])
                else:
                    print("Invalid choice. Please enter a number from 0 to 18.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        print('\n')
