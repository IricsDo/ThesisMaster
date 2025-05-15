import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os


def plot_loss(new_directory):
    try:
        curve_file = os.path.join(new_directory, "lcurve.out")
        with open(curve_file) as f:
            headers = f.readline().split()[1:]

        lcurve = pd.DataFrame(np.loadtxt(curve_file), columns=headers)
        legends = ["rmse_e_val", "rmse_e_trn", "rmse_f_val", "rmse_f_trn"]
        for legend in legends:
            plt.loglog(lcurve["step"], lcurve[legend], label=legend)
        plt.legend()
        plt.xlabel("Training steps")
        plt.ylabel("Loss")
        plt.plot()
        plt.savefig(os.path.join(new_directory, "output_loss.png"))
        plt.close()
    except Exception as e:
        raise Exception("Can not plot the loss of model after training")
