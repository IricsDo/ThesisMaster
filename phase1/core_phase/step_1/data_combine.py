import numpy as np
import os
from utils.folder_utils import create_folder, copy_one_file

def combine_npy_files(folder_data : list[str], output_folder : str, verbose : bool = False) -> bool:

    new_output_folder = os.path.join(output_folder, 'set.000')
    create_folder(new_output_folder)
    copy_one_file(os.path.join(folder_data[0], 'type.raw'), os.path.join(output_folder, 'type.raw'))
    copy_one_file(os.path.join(folder_data[0], 'type_map.raw'), os.path.join(output_folder, 'type_map.raw'))

    npy_files = ['virial.npy', 'force.npy', 'energy.npy', 'coord.npy', 'box.npy']

    for data_type in npy_files:
        data_combine = list()
        for folder in folder_data:
                data_combine.append(np.load(os.path.join(folder, 'set.000', data_type)))
        
        if all(arr.shape == data_combine[0].shape for arr in data_combine):
            combined_data = np.vstack(data_combine)
            np.save(os.path.join(new_output_folder, data_type), combined_data)
        else:
            raise ValueError("Arrays have different shapes and cannot be stacked.")
        
        if verbose:
            print(f'Combined {data_type} and saved to {new_output_folder}')

    return True

def combine(new_directory : str, train_val_folders : list) -> None:
    training_folders = [os.path.join(new_directory, folder[0]) for folder in train_val_folders]
    validation_folders = [os.path.join(new_directory, folder[1]) for folder in train_val_folders]

    # Run the combine_npy_files function for both training and validation folders using threading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(combine_npy_files, training_folders, os.path.join(new_directory, 'training_data'), True),
            executor.submit(combine_npy_files, validation_folders, os.path.join(new_directory,'validation_data'), True)
        ]
        
        # Wait for all threads to finish and handle any exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # This will raise an exception if the function encountered one
            except Exception as exc:
                print(f"Generated an exception: {exc}")

    print("All files for both training and validation data have been combined and saved.")

if __name__ == '__main__':
    from phase1.core_phase.step_1.data_scanning import scan, KEY_WORD_DATA_FOLDER
    from phase1.core_phase.step_1.data_creation import creation
    from utils.folder_utils import create_folder
    import concurrent.futures

    # Step 1.1
    data_directory = r'E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_in'
    folders = scan(data_directory)

    # Step 1.2
    new_directory = r'E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out'
    train_val_folders = creation(new_directory, folders)

    # Step 1.3
    combine(new_directory, train_val_folders)   