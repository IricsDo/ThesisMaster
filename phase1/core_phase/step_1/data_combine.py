import os
import numpy as np
import concurrent.futures

from utils.folder_utils import create_folder, copy_one_file
from utils_com.logger import ServerLogger


def combine_npy_files(
    folder_data: list[str], output_folder: str, verbose: bool = False
) -> bool:

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

        if all(arr.shape == data_combine[0].shape for arr in data_combine):
            combined_data = np.vstack(data_combine)
            np.save(os.path.join(new_output_folder, data_type), combined_data)
        else:
            raise ValueError("Arrays have different shapes and cannot be stacked.")


        if verbose:
            LOGGER.log(f"Combined {data_type} and saved to {new_output_folder}")

    return True


def combine(new_directory: str, data_folders: list, verbose: bool = False) -> None:
    if not data_folders:
        raise Exception("The list data not include train and val folder")

    LOGGER = ServerLogger()

    training_folders = [
        os.path.join(new_directory, folder[0]) for folder in data_folders
    ]
    validation_folders = [
        os.path.join(new_directory, folder[1]) for folder in data_folders
    ]

    # Run the combine_npy_files function for both training and validation folders using threading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                combine_npy_files,
                training_folders,
                os.path.join(new_directory, "training_data"),
                False,
            ),
            executor.submit(
                combine_npy_files,
                validation_folders,
                os.path.join(new_directory, "validation_data"),
                False,
            ),
        ]

        # Wait for all threads to finish and handle any exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # This will raise an exception if the function encountered one
            except Exception as exc:
                LOGGER.log(f"Combine data an exception: {exc}")

    if verbose:
        LOGGER.log(
            f"All files for both training and validation data have been combined and saved in {new_directory}"
        )


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
