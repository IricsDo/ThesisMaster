import json
from utils.folder_utils import delete_file

# Function to modify the JSON file
def modify(source_file : str, new_file : str, type_map_value : str, training_systems : str, validation_systems : str, disp_file_value : str) -> None:

    # Open and load the JSON data
    with open(source_file, 'r') as f:
        data = json.load(f)
    
    # Modify the values
    data['model']['type_map'] = type_map_value
    data['training']['training_data']['systems'] = training_systems
    data['training']['validation_data']['systems'] = validation_systems
    data['training']['disp_file'] = disp_file_value
    
    # Write the updated data back to the JSON file
    with open(new_file, 'w') as f:
        json.dump(data, f, indent=4)

    
def setup_training_input(source_file : str, new_file : str, type_map_value : str, training_systems : str, validation_systems : str, disp_file_value : str) -> None:

    delete_file(new_file)
    delete_file(disp_file_value)
    modify(source_file, new_file, type_map_value, training_systems, validation_systems, disp_file_value)

    
if __name__ == '__main__':
    # Step 2    
    source_file =r'E:\Work Spaces\Thesis\Code\Thes, isMaster\phase1\config\input.json'
    new_file = r'E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out\input.json'
    type_map_value = ["C", "H"]  
    training_systems = [r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out\training_data"]  
    validation_systems = [r"E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out\validation_data"] 
    disp_file_value = r'E:\Work Spaces\Thesis\Code\ThesisMaster\data_test_out\lcurve.out'
    setup_training_input(source_file, new_file, type_map_value, training_systems, validation_systems, disp_file_value)
