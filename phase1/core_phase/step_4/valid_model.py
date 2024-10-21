import dpdata
import matplotlib.pyplot as plt
import numpy as np


def vaild(new_directory : str) -> None:
    training_systems = dpdata.LabeledSystem(os.path.join(new_directory , "validation_data"), fmt = "deepmd/npy")
    predict = training_systems.predict(os.path.join(new_directory , "graph.pb"))

    plt.scatter(training_systems["energies"], predict["energies"])
    x_range = np.linspace(plt.xlim()[0], plt.xlim()[1])

    plt.plot(x_range, x_range, "r--", linewidth = 0.25)
    plt.xlabel("Energy of DFT")
    plt.ylabel("Energy predicted by deep potential")
    plt.plot()
    plt.savefig(os.path.join(new_directory , 'output_predict.png'))

if __name__ == '__main__':
    import os
    # Step 4.3
    new_directory = r'E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out'
    vaild(new_directory)
