import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_loss(new_directory):
    try:
        curve_file = os.path.join(new_directory, 'lcurve.out')
        with open(curve_file) as f:
            headers = f.readline().split()[1:]

        lcurve = pd.DataFrame(np.loadtxt(curve_file), columns =  headers)
        legends = ["rmse_e_val", "rmse_e_trn", "rmse_f_val" , "rmse_f_trn" ]
        for legend in legends:
            plt.loglog(lcurve["step"], lcurve[legend], label = legend )
        plt.legend()
        plt.xlabel("Training steps")
        plt.ylabel("Loss")
        plt.show()
        plt.savefig(os.path.join(new_directory, 'output_loss.png'))

    except Exception as e:
        raise BaseException('Can not plot the loss of model after training')

if __name__ == '__main__':

    # Step 3.2
    new_directory = r'E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out'
    plot_loss(new_directory)