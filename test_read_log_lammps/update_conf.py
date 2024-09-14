def update_conf_lmp(input_file, output_file, new_positions, type_map):
    """
    Updates the atomic positions (x, y, z) and atom types in a LAMMPS configuration file.
    
    Args:
        input_file (str): Path to the original conf.lmp file.
        output_file (str): Path to save the new conf.lmp file with updated positions.
        new_positions (list of dict): A list of dictionaries containing 'type', 'x', 'y', 'z' for each atom.
                                      Each dictionary should have keys 'type', 'x', 'y', 'z'.
    """

    
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    # Locate the section where atom positions start ("Atoms # atomic")
    atom_start_idx = None
    for i, line in enumerate(lines):
        if line.startswith("Atoms"):
            atom_start_idx = i + 2  # Atom positions start 2 lines after "Atoms # atomic"
            break

    if atom_start_idx is None:
        raise ValueError("Could not find 'Atoms' section in the input file.")

    # Create the output file and write the header (everything before atom positions)
    with open(output_file, 'w') as outfile:
        # Write the header (until the atom section)
        for line in lines[:atom_start_idx]:
            outfile.write(line)

        # Write the updated atom positions
        for i, line in enumerate(lines[atom_start_idx:]):
            atom_data = line.split()
            atom_id = atom_data[0]  # First value is the atom id
            # Use the new type and positions from the new_positions list
            new_type = type_map[new_positions[i]['type']]
            new_x = float(new_positions[i]['x'])
            new_y = float(new_positions[i]['y'])
            new_z = float(new_positions[i]['z'])

            # Ensure the spacing is consistent with your format
            outfile.write(f"{atom_id:>6} {new_type:>6} {new_x:>13.10f} {new_y:>13.10f} {new_z:>13.10f}\n")


if __name__ == "__main__":
    # Example usage
    input_file = 'conf.lmp'  # Path to the original conf.lmp
    output_file = 'updated_conf.lmp'  # Path to the new conf.lmp

    # Example new positions (your actual list)
    new_positions = [
        {'type': 'H', 'x': 4.314243368333564, 'y': 3.8712114114388005, 'z': 5.211287059836614},
        {'type': 'H', 'x': 5.134952113163232, 'y': 4.447225727735065, 'z': 3.512989189345559},
        {'type': 'C', 'x': 5.300100846976108, 'y': 4.93307694914902, 'z': 4.664836177290672},
        {'type': 'H', 'x': 6.331179691469967, 'y': 4.6074965876812755, 'z': 4.773070347973773},
        {'type': 'H', 'x': 4.639186563732688, 'y': 5.9049988862542016, 'z': 4.637549000593256}
    ]
    # Define the type mapping (H -> 1, C -> 2)
    type_map = {'H': '1', 'C': '2'}

    # Update the conf.lmp file with new positions
    update_conf_lmp(input_file, output_file, new_positions, type_map)

    print(f"New positions have been written to {output_file}")
