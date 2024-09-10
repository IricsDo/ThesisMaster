import pandas as pd

import json

# Function to read type_map.raw and create a mapping
def read_type_map(file_path):
    """
    Reads the type_map.raw file and returns a dictionary mapping type numbers to atom types.
    """
    type_map = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if len(lines) >= 2:
            type_map[1] = lines[0].strip()  # H
            type_map[2] = lines[1].strip()  # C
    return type_map

def read_lammps_dump(file_path):
    """
    Reads a LAMMPS dump file and returns a dictionary where each timestep is a key.
    Each value is a DataFrame containing 'id', 'type', 'x', 'y', 'z' for all atoms in that timestep.
    """
    timesteps_data = {}
    timestep = None
    atom_data = []
    columns = []

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()

            # Detect start of a new timestep
            if line.startswith("ITEM: TIMESTEP"):
                if timestep is not None and atom_data:
                    # Save the previous timestep's atom data into a DataFrame
                    timesteps_data[timestep] = pd.DataFrame(atom_data, columns=columns)
                
                # Read the new timestep
                timestep = int(next(file).strip())
                atom_data = []
                columns = []

            # Read number of atoms (can be skipped if not needed)
            elif line.startswith("ITEM: NUMBER OF ATOMS"):
                num_atoms = int(next(file).strip())

            # Read box bounds (can be skipped or stored if needed)
            elif line.startswith("ITEM: BOX BOUNDS"):
                for _ in range(3):
                    next(file)

            # Read atomic data headers
            elif line.startswith("ITEM: ATOMS"):
                columns = line.split()[2:]  # Get the headers (id, type, x, y, z)

            # Read atomic data
            else:
                atom_data.append(line.split())

        # Save the last timestep's atom data into a DataFrame
        if timestep is not None and atom_data:
            timesteps_data[timestep] = pd.DataFrame(atom_data, columns=columns)

    return timesteps_data

# def extract_atom_data(timesteps_data):
#     """
#     Extracts 'id', 'type', 'x', 'y', 'z' data for each timestep and concatenates them.
#     Returns a DataFrame containing this data for all timesteps.
#     """
#     extracted_data = []

#     for timestep, data in timesteps_data.items():
#         data['timestep'] = timestep  # Add a timestep column
#         extracted_data.append(data[['timestep', 'id', 'type', 'x', 'y', 'z']])

#     # Concatenate data for all timesteps into a single DataFrame
#     return pd.concat(extracted_data, ignore_index=True)

def extract_atom_data(timesteps_data, type_map):
    """
    Extracts 'id', 'type', 'x', 'y', 'z' data for each timestep and maps 'type' using type_map.
    Returns a list of dictionaries with 'timestep' and 'atoms' for each timestep.
    """
    mapped_atom_data = []

    for timestep, data in timesteps_data.items():
        atom_list = [
            {
                "type": type_map[int(row['type'])],  # Map the type using type_map
                "x": float(row['x']),
                "y": float(row['y']),
                "z": float(row['z'])
            }
            for _, row in data.iterrows()
        ]
        mapped_atom_data.append({
            "timestep": timestep,
            "atoms": atom_list
        })

    return mapped_atom_data

if __name__ == '__main__':
    # Example usage:
    lammps_file = 'ch4.dump'  # Path to your LAMMPS dump file
    type_map_file = 'type_map.raw'  # Path to your type_map.raw file

    # Read LAMMPS dump and type map files
    timesteps = read_lammps_dump(lammps_file)
    type_map = read_type_map(type_map_file)

    # Extract and map atom data
    mapped_atom_data = extract_atom_data(timesteps, type_map)
    print(mapped_atom_data)
