import os
import dpdata
import numpy as np
import concurrent.futures

from utils.folder_utils import create_folder, copy_one_file
from utils_com.logger import ServerLogger


def combine_npy_files(
    folder_data: list[str], output_folder: str, verbose: bool = False
) -> None:

    new_output_folder = os.path.join(output_folder, "set.000")
    create_folder(new_output_folder)
    copy_one_file(
        os.path.join(folder_data[0], "type.raw"),
        os.path.join(output_folder, "type.raw"),
    )
    copy_one_file(
        os.path.join(folder_data[0], "type_map.raw"),
        os.path.join(output_folder, "type_map.raw"),
    )
    LOGGER = ServerLogger()

    npy_files = ["virial.npy", "force.npy", "energy.npy", "coord.npy", "box.npy"]

    for data_type in npy_files:
        data_combine = list()
        for folder in folder_data:
            data_combine.append(np.load(os.path.join(folder, "set.000", data_type)))

        # if all(arr.shape == data_combine[0].shape for arr in data_combine):
        #     combined_data = np.vstack(data_combine)
        #     np.save(os.path.join(new_output_folder, data_type), combined_data)
        
        if data_combine:
            # Temp fix incorrect shape of data
            # Truncate to the smallest number of columns
            min_cols = min(arr.shape[1] for arr in data_combine)
            data_combine_aligned = [arr[:, :min_cols] for arr in data_combine]
            combined_data = np.vstack(data_combine_aligned)
            np.save(os.path.join(new_output_folder, data_type), combined_data)
        else:
            raise ValueError("The list is empty shapes. Cannot be stacked.")


        if verbose:
            LOGGER.log(f"Combined {data_type} and saved to {new_output_folder}")

    return

def combine_dp_system(
    folder_data: dict, output_folder: str, verbose: bool = False
) -> None:
    dict_dp_data = {}
    for key, value in folder_data.items():
        data = dpdata.LabeledSystem()
        for v in value:
            data.extend(dpdata.LabeledSystem(v, fmt="deepmd/npy"))
        if key not in dict_dp_data.keys():
            dict_dp_data[key] = data
    
    return

def combine(new_directory: str, data_folders: list, verbose: bool = False) -> list[dict]:
    if not data_folders:
        raise Exception("The list data not include train and val folder")

    LOGGER = ServerLogger()

    training_folders = {}
    validation_folders = {}

    try:
        for it in data_folders:
            for key, value in it.items():
                if key not in training_folders.keys():
                    training_folders[key] = [os.path.join(new_directory, value[0])]
                else:
                    training_folders[key].append(os.path.join(new_directory, value[0]))

                if key not in validation_folders.keys():
                    validation_folders[key] = [os.path.join(new_directory, value[1])]
                else:
                    validation_folders[key].append(os.path.join(new_directory, value[1]))
    except Exception as exc:
        LOGGER.log(f"Combine data an exception: {exc}")

    # Run the function for both training and validation folders using threading
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     futures = [
    #         executor.submit(
    #             combine_dp_system,
    #             training_folders,
    #             os.path.join(new_directory, "training_data"),
    #             False,
    #         ),
    #         executor.submit(
    #             combine_dp_system,
    #             validation_folders,
    #             os.path.join(new_directory, "validation_data"),
    #             False,
    #         ),
    #     ]

    #     # Wait for all threads to finish and handle any exceptions
    #     for future in concurrent.futures.as_completed(futures):
    #         try:
    #             future.result()  # This will raise an exception if the function encountered one
    #         except Exception as exc:
    #             LOGGER.log(f"Combine data an exception: {exc}")

    if verbose:
        LOGGER.log(
            f"All files for both training and validation data have been combined and saved in {new_directory}"
        )

    return [training_folders, validation_folders]

if __name__ == "__main__":
    from phase1.core_phase.step_1.data_scanning import scan, KEY_WORD_DATA_FOLDER
    from phase1.core_phase.step_1.data_creation import creation
    from utils.folder_utils import create_folder

    # Step 1.1
    data_directory = r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_in"
    folders = scan(data_directory)

    # Step 1.2
    new_directory = r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out"
    train_val_folders = creation(new_directory, folders)

    # Step 1.3
    combine(new_directory, train_val_folders)
