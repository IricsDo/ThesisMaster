from utils.folder_utils import create_folder, move_many_to_one
import os


def collect_data_to_one(destination_path: str, type_of_data: str, data_path: list[str]) -> str:
    new_path = os.path.join(destination_path, type_of_data)
    create_folder(new_path)
    move_many_to_one(data_path, new_path, True)
    return new_path
