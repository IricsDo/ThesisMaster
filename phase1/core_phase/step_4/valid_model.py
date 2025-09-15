import os
import dpdata
import numpy as np
import matplotlib.pyplot as plt

from utils_com.logger import ServerLogger


def vaild(
    new_directory: str,
    new_path: str,
    model_path: str = "",
    tesorflow_fw: bool = True,
    pytorch_fw: bool = False,
    task_predict: bool = False,
) -> None:

    LOGGER = ServerLogger()

    if tesorflow_fw and pytorch_fw:
        raise Exception("Backend not vaild!")
    try:
        for data in os.listdir(new_path):
            data_path = os.path.join(new_path, data)
            if not os.path.isdir(data_path):
                LOGGER.log(f"{data_path} not vaild, find another file")
                continue
            systems = dpdata.LabeledSystem(
                data_path,
                fmt="deepmd/npy",
            )
            predict = None

            if task_predict and model_path:
                predict = systems.predict(
                    os.path.join(
                        model_path, "graph.pb" if tesorflow_fw else "graph.pth"
                    )
                )
            else:
                predict = systems.predict(
                    os.path.join(
                        new_directory, "graph.pb" if tesorflow_fw else "graph.pth"
                    )
                )

            plt.scatter(systems["energies"], predict["energies"])
            x_range = np.linspace(plt.xlim()[0], plt.xlim()[1])

            plt.plot(x_range, x_range, "r--", linewidth=0.25)
            plt.xlabel("Energy of DFT")
            plt.ylabel("Energy predicted by deep potential")
            plt.plot()
            plt.savefig(
                os.path.join(
                    new_path if task_predict else new_directory,
                    f"output_with_{'predict_' + os.path.basename(data_path) if task_predict else os.path.basename(data_path)}.png",
                )
            )
            plt.close()
    except Exception as e:
        raise Exception("Can not complete the vaildation in model")


def predict(
    predict_directory: str,
    new_path: str,
    model_path: str,
    tesorflow_fw: bool,
    pytorch_fw: bool,
    task_predict: bool,
) -> None:
    vaild(
        predict_directory, new_path, model_path, tesorflow_fw, pytorch_fw, task_predict
    )
