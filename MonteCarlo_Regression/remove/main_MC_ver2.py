# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 15:44:20 2021

@author: Nguyen Van Hoa

This module simulates hydrogen adsorption using a Monte Carlo method.
It includes functions for calculating energy and performing simulations.
"""

import ThesisMaster.MonteCarlo_Regression.remove.module_ver2 as md
import numpy as np
import random as rd
import math
import time 
import pandas as pd
from joblib import Parallel, delayed

# Constants
kB = 8.6173324e-5  # Boltzmann constant in eV/K

# Unit cell and lattice dimensions
a = 4  # Length of Pt(100)-(1x1) unit cell
b = 2
c = 1
n_x = 10  # Number of unit cells along x-axis
n_y = 10  # Number of unit cells along y-axis
len_x = n_x * a
len_y = n_y * a

# Temperature and simulation parameters
T = 303  # Temperature in Kelvin
nequiv = 10000  # Number of equilibration steps
nmeasure = 10e6  # Number of measurement steps
ntot = int(nequiv + nmeasure)

# Hydrogen site and interaction energy parameters
h_unit_site = [[0, 1, 1], [0, 3, 3], [1, 3, 1], [1, 1, 3]]  # Hydrogen unit sites
E_site = [-0.79894, -0.79894]  # Site energies for different site types
# E_int = [0.0625, 0.0202, 0.0161, 0.0131, 0.0061, 0.0077, -0.0172]  # Interaction energies
E_int = [0.060728968634255566, 0.021656454628845037, 0.014815471617979198, 0.012432355215369258, 0.006358444158441091, 0.005580559734457011, -0.013997341101679505]

# Initialize lattice
lattice_vector = [0, a, a]
empty_pos = md.generate_lattice(h_unit_site, lattice_vector, n_x, n_y)
flag = np.zeros([3 * len_x, 3 * len_y], dtype=int)
max_H = n_x * n_y * len(h_unit_site)

# Output labels
label = ['Temp', 'Loading', 'Ave Eng', 'Accept Rate', 'Vint1', 'Vint2', 'Vint3', 'Vint4', 'Vint5', 'Vint6', 'Vint7', 'runtime']

def calculate_at_numH(num_H):
    print(f"-------------------> Starting calculate with H = {num_H} ...")
    start_time = time.time()
    accept_rate = 0
    sum_energy = 0
    E_corr = np.zeros(len(E_int), dtype=float)

    # Initialize lattice and hydrogen positions
    empty_pos = md.generate_lattice(h_unit_site, lattice_vector, n_x, n_y)
    flag = np.zeros([3 * len_x, 3 * len_y], dtype=int)
    H_pos = []  # List of hydrogen positions
    while len(H_pos) < num_H:
        H_pos, flag, empty_pos = md.add_hydrogen_randomly(H_pos, flag, empty_pos)
    
    # Calculate initial energy
    E_corr_last = np.zeros(len(E_int), dtype=float)
    energy_last = 0
    for i in H_pos:
        _, E_int_h, energy_h = md.calculate_energy(i, flag)
        E_corr_last += E_int_h * 0.5
        energy_last += energy_h
    energy_last -= np.sum(E_corr_last)
    
    # Pre-generate random numbers for Boltzmann factor checks
    random_numbers = np.random.random(ntot)
    
    # Monte Carlo loop: shifting hydrogen to another position
    for step in range(ntot):
        H_pos_temp = list(H_pos)
        flag_temp = np.array(flag, dtype=int)
        empty_pos_temp = list(empty_pos)
        energy_last_temp = energy_last
        E_corr_last_temp = np.array(E_corr_last, dtype=float)
        
        h_moved = H_pos[rd.randrange(0, num_H)]
        _, E_int_moved, E_h_moved = md.calculate_energy(h_moved, flag)
        E_corr_check = E_corr_last - E_int_moved
        energy_check = energy_last - E_h_moved
        H_pos, flag, empty_pos = md.remove_hydrogen(h_moved, H_pos, flag, empty_pos)
        H_pos, flag, empty_pos = md.add_hydrogen_randomly(H_pos, flag, empty_pos)
        _, E_int_added, E_h_added = md.calculate_energy(H_pos[-1], flag)
        E_corr_check += E_int_added
        energy_check += E_h_added
        
        if energy_check <= energy_last:
            E_corr_last = np.array(E_corr_check, dtype=float)
            energy_last = energy_check
            rate = 1
        else:
            wt = math.exp((energy_last - energy_check) / (kB * T))
            if random_numbers[step] <= wt:
                E_corr_last = np.array(E_corr_check, dtype=float)
                energy_last = energy_check
                rate = 1
            else:
                H_pos = list(H_pos_temp)
                empty_pos = list(empty_pos_temp)
                flag = np.array(flag_temp, dtype=int)
                energy_last = energy_last_temp
                E_corr_last = np.array(E_corr_last_temp, dtype=float)
                rate = 0

        if step >= nequiv:
            accept_rate += rate
            sum_energy += energy_last
            E_corr += E_corr_last
    
    end_time = time.time()
    print(T, num_H, end_time - start_time)
    
    temp = [T, num_H, sum_energy / nmeasure, accept_rate / nmeasure]
    temp.extend(E_corr / nmeasure)
    temp.append(end_time - start_time)
    df = pd.DataFrame([temp], columns=label)
    df.to_csv(fol_name, mode='a', index=None, header=None)

# Main execution
fol_name = f'{n_x}x{n_y}_{T}_MD_{int(nmeasure)}testing.csv'
df = pd.DataFrame(np.zeros((1, len(E_int) + 5), dtype=int))
df.to_csv(fol_name, header=label, index=False)

# import multiprocessing
# # Get the number of CPU cores available
# num_cores = multiprocessing.cpu_count()
# print(f"Number of CPU cores available: {num_cores}")
Parallel(n_jobs=1)(delayed(calculate_at_numH)(num_H) for num_H in range(1, 101))
