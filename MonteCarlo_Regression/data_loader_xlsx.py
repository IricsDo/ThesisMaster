import pandas as pd

class DataLoader():
    def __init__(self, path : str) -> None:
        self.df = pd.read_excel(path, sheet_name="Data")

    def prepare_data(self):
        if self.df.empty:
            return
        
        columns_to_include = ['E_int', 'b1a', 'b12', 'b1b', 'b13', 'b4a', 'b19', 'b19b']
        self.sub_df = self.df[columns_to_include]
        X = self.sub_df.drop(columns=['E_int']).iloc[0:52]
        y = self.sub_df['E_int'].iloc[0:52]

        # print(X,y)
        return X, y

