import re

def extract_lammps_last_energy(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
    # Pattern for the header line with the columns: Step, PotEng, KinEng, TotEng, Temp, Press, Volume
    header_pattern = re.compile(r"\s*Step\s+PotEng\s+KinEng\s+TotEng\s+Temp\s+Press\s+Volume")
    # Pattern for lines with the actual data
    data_pattern = re.compile(r"\s*(\d+)\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)")

    found_header = False
    last_data_line = None

    for line in lines:
        # Search for the header line
        if not found_header and header_pattern.search(line):
            found_header = True  # Once header is found, set flag
            continue
        
        # Once the header is found, look for the matching data lines
        if found_header:
            match = data_pattern.match(line)
            if match:
                last_data_line = match.groups()  # Save the most recent matching data line

    if last_data_line:
        step, poteng, kineng, toteng, temp, press, volume = last_data_line
        # print(f"Last data line extracted: Step: {step}, PotEng: {poteng}, KinEng: {kineng}, TotEng: {toteng}, Temp: {temp}, Press: {press}, Volume: {volume}")
        # return step, poteng, kineng, toteng, temp, press, volume
        return poteng
    else:
        raise ValueError("Data not found in the file.")

if __name__ == '__main__':
    # Call the function on your LAMMPS log file
    file_path = "log.lammps"
    extract_lammps_last_energy(file_path)
