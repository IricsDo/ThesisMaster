import numpy as np

class DataLoader():
    def __init__(self, path : str) -> None:
        self.npy = np.load(path)

    def prepare_data(self):
        # print(f'Size of array: { np.shape(self.npy) }')
        return self.npy
    
if __name__ == '__main__':
    dt = DataLoader(r'CNN_Regression\data\training_data\set.000\coord.npy')
    dt.prepare_data()

