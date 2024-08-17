from lazypredict.Supervised import LazyRegressor
from sklearn.model_selection import train_test_split

class LazyRegressorModule():
    def __init__(self) -> None:
        self.lzy_model = LazyRegressor(verbose=0, ignore_warnings=True, custom_metric=None, predictions=True, regressors = 'all')
        self.X = None
        self.y = None

    def set_data(self, X, y) -> None:
        self.X = X
        self.y = y

    def run_lazy_regressor(self):
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        reg_models, predictions = self.lzy_model.fit(X_train, X_test, y_train, y_test)
        print(reg_models)
        print('\n')
        print(predictions)