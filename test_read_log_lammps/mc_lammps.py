#!/usr/bin/env python
import random, math, subprocess, os, shutil, time, json, sys
from extract_eng import extract_lammps_last_energy
from extract_pos import read_lammps_dump, read_type_map, extract_atom_data
from update_conf import update_conf_lmp
from datetime import datetime

# Set these parameters
nloop = 100

deltaperturb = 0.02 # A
deltamove = 0.01 # A

kb = 8.6173303e-5 #eV/K
T = 300 # K

random.seed(27848)

NAME_COMPOUND = "CH4"

def report(model_name : str = '', temperture : str = '', mc_step : str = '', start_time : str = '', end_time : str = '', execu_time : str = '', number_of_atom : dict = {}, start_energy : str = '', end_energy : str = '', naccept : str = ''):
    if not model_name or not bool(number_of_atom) or not start_energy or not end_energy:
        print("\nMissing value requirement, at least: model_name & number_of_atom & start_energy & end_energy")
    
    with open('report.txt', 'w') as f:
        data = [model_name, json.dumps(number_of_atom), temperture, mc_step, start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S"), str(execu_time), start_energy, end_energy, naccept]
        f.write(f"Model name: {data[0]}\n")
        f.write(f"Number of atom: {data[1]}\n")
        f.write(f"Temperture: {data[2]} K\n")
        f.write(f"Start time: {data[4]}\n")
        f.write(f"End time: {data[5]}\n")
        f.write(f"Execu time: {data[6]}\n")
        f.write(f"Start energy: {data[7]}\n")
        f.write(f"End energy: {data[8]}\n")
        f.write(f"MC loop: {data[3]}\n")
        f.write(f"MC execu loop: {data[9]}\n")


    
def backup(path : str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        shutil.copy('conf.lmp', path)
        shutil.copy('ch4.dump', path)
        shutil.copy('log.lammps', path)
    


def run_lammps(input_file : str, debug=True):
    if debug:
        return
    """ Run LAMMPS with a given input file and output results to a given file """
    try:
        result = subprocess.run(['lmp', '-i', 'in.lammps'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        sys.exit(-1)

        
if __name__ == '__main__':

    ani_report = list()
    mde_report = list()

    # Start time
    start_time = datetime.now()
    # Run initial LAMMPS simulation to get initial energy and positions
    print(f"{time.time()} >Get PE from lammps")
    run_lammps(infile)
    initial_energy = extract_lammps_last_energy(file_log_path)
    print(f"{time.time()} >Get PE from lammps: Done")

    print(f"{time.time()} >Backup file: conf.lmp, ch4.dump, log.lammps")

    backup('backup_conf')

    print(f"{time.time()} >Read all data file")

    infile = 'in.lammps'
    file_log_path = "log.lammps"
    conf_file = "conf.lmp"

    # Disorder the system
    dumpy_file = 'ch4.dump'  # Path to your LAMMPS dump file
    type_map_file = 'type_map.raw'  # Path to your type_map.raw file

    # Read LAMMPS dump and type map files
    timesteps = read_lammps_dump(dumpy_file)
    type_map = read_type_map(type_map_file)

    # Extract and map atom data
    mapped_atom_data = extract_atom_data(timesteps, type_map)
    positions = mapped_atom_data[-1]
    natoms = len(positions['atoms'])
    print(f"{time.time()} >Read all data file: Done")

    print(f"{time.time()} Init position")
    for i in range(natoms):
        print(f"{positions['atoms'][i]['type']}")
        print(f"{positions['atoms'][i]['x']}")
        print(f"{positions['atoms'][i]['y']}")
        print(f"{positions['atoms'][i]['z']}")
        print("\n")


    # Run MC loop
    elast = initial_energy
    naccept = 0
    print(f"{time.time()} >Start MC")
    mde_report.append(f"# {'Step':<8}{'T (K)':<10}{'E_Pot (eV)':<12}")

    for i in range(nloop):
        previous_positon = positions

        # Pick random one atom
        iatom = random.randrange(0, natoms)

        print(f"{time.time()} >Previous position")
        print(f"{previous_positon['atoms'][iatom]['type']}")
        print(f"{previous_positon['atoms'][iatom]['x']}")
        print(f"{previous_positon['atoms'][iatom]['y']}")
        print(f"{previous_positon['atoms'][iatom]['z']}")

        x0, y0, z0 = [positions['atoms'][iatom]['x'], positions['atoms'][iatom]['y'], positions['atoms'][iatom]['z']]

        positions['atoms'][iatom]['x'] = f"{float(positions['atoms'][iatom]['x']) + (2 * deltamove * random.random() - 1):.5f}"
        positions['atoms'][iatom]['y'] = f"{float(positions['atoms'][iatom]['y']) + (2 * deltamove * random.random() - 1):.5f}"
        positions['atoms'][iatom]['z'] = f"{float(positions['atoms'][iatom]['z']) + (2 * deltamove * random.random() - 1):.5f}"

        print(f"{time.time()} >Random one atom position")
        print(f"\t{positions['atoms'][iatom]['type']}")
        print(f"{positions['atoms'][iatom]['x']}")
        print(f"{positions['atoms'][iatom]['y']}")
        print(f"{positions['atoms'][iatom]['z']}")

        # Write new conf.lmp
        update_conf_lmp(conf_file, conf_file, positions['atoms'], {v: str(k) for k, v in type_map.items()})

        # Run LAMMPS and get energy with new conf.lmp
        run_lammps(infile)
        energy = extract_lammps_last_energy(file_log_path)

        is_accept = False
        if energy <= elast:
            elast = energy
            naccept += 1
            is_accept = True
        elif random.random() <= math.exp((float(elast) - float(energy)) / (kb*T)):
            elast = energy
            naccept += 1
            is_accept = True
        else:
            positions['atoms'][iatom]['x'] = previous_positon[iatom]['x']
            positions['atoms'][iatom]['y'] = previous_positon[iatom]['y']
            positions['atoms'][iatom]['z'] = previous_positon[iatom]['z']

        print(f"\t{previous_positon['atoms'][iatom]['type']}   \t\t\t{positions['atoms'][iatom]['type']}")
        print(f"x:{previous_positon['atoms'][iatom]['x']}      x:{positions['atoms'][iatom]['x']}")
        print(f"y:{previous_positon['atoms'][iatom]['y']}      y:{positions['atoms'][iatom]['y']}")
        print(f"z:{previous_positon['atoms'][iatom]['z']}      z:{positions['atoms'][iatom]['z']}")

        print(f"{time.time()} >Loop {i+1}/{nloop}: Current energy is {energy}, energy last is {elast} => {'Accept' if is_accept else 'Keep'}")

        ani_report.append(f'{natoms:>5}')
        ani_report.append('')
        for j in range(natoms):
            ani_report.append(f'{positions['atoms'][j]['type']:<8}{positions['atoms'][j]['x']:<12}{positions['atoms'][j]['y']:<12}{positions['atoms'][j]['z']:<12}')

        mde_report.append(f"{i:<8}{T:<10}{elast:<15}")

    # End time
    end_time = datetime.now()

    # Final energy and stats
    print("\n\nMC stats:")
    print(f"  starting energy = {initial_energy}")
    print(f"  final energy = {elast}")
    print(f"  accepted MC moves = {naccept}")
    print(f"  time execute = {end_time - start_time}")

    report(NAME_COMPOUND, str(T), str(nloop), start_time, end_time, end_time - start_time, {'C': 1, 'H' : 4}, initial_energy, elast, str(naccept))

    with open(f'{NAME_COMPOUND}.ANI', 'w') as file:
        for line in ani_report:
            file.write(line + '\n')

    with open(f'{NAME_COMPOUND}.MDE', 'w') as file:
        for line in mde_report:
            file.write(line + '\n')