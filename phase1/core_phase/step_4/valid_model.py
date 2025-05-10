import os
import dpdata
import numpy as np
import matplotlib.pyplot as plt


def vaild(
    new_directory: str, new_path: str, model_path: str = "",  tesorflow_fw: bool = True, pytorch_fw: bool = False, task_predict: bool = False
) -> None:
    
    if tesorflow_fw and pytorch_fw:
        raise Exception("Backend not vaild!")
    try:
        for data in os.listdir(new_path):
            data_path = os.path.join(new_path, data)
            training_systems = dpdata.LabeledSystem(
                data_path,
                fmt="deepmd/npy",
            )
            predict = None

            if task_predict and model_path:
                predict = training_systems.predict(os.path.join(model_path, "graph.pb" if tesorflow_fw else "graph.pth"))
            else:
                predict = training_systems.predict(
                    os.path.join(new_directory, "graph.pb" if tesorflow_fw else "graph.pth")
                )

            plt.scatter(training_systems["energies"], predict["energies"])
            x_range = np.linspace(plt.xlim()[0], plt.xlim()[1])

            plt.plot(x_range, x_range, "r--", linewidth=0.25)
            plt.xlabel("Energy of DFT")
            plt.ylabel("Energy predicted by deep potential")
            plt.plot()
            plt.savefig(
                os.path.join(
                    new_path if task_predict else new_directory,
                    f"output_with_{'prediction_data' if task_predict else os.path.basename(data_path)}.png",
                )
            )
            plt.close()
    except Exception as e:
        raise Exception("Can not complete the vaildation in model")


def predict(
    predict_directory: str, new_path: str, model_path: str, tesorflow_fw: bool, pytorch_fw: bool, task_predict: bool
) -> None:
    vaild(predict_directory, new_path, model_path, task_predict, tesorflow_fw, pytorch_fw)


if __name__ == "__main__":
    # Step 4.3
    new_directory = r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out"
    vaild(new_directory)
