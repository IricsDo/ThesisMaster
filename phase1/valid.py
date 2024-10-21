import dpdata

training_systems = dpdata.LabeledSystem("training_data", fmt = "deepmd/npy")
predict = training_systems.predict("graph.pb")

import matplotlib.pyplot as plt
import numpy as np

plt.scatter(training_systems["energies"], predict["energies"])

x_range = np.linspace(plt.xlim()[0], plt.xlim()[1])

plt.plot(x_range, x_range, "r--", linewidth = 0.25)
plt.xlabel("Energy of DFT")
plt.ylabel("Energy predicted by deep potential")
plt.plot()
plt.savefig('output_predict.png')