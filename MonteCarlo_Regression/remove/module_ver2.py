# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 15:06:43 2021

@author: Nguyen Van Hoa

This module simulates hydrogen adsorption on a surface. 
It includes functions for lattice generation, hydrogen addition/removal, and energy calculation.
"""

import numpy as np
import random as rd
import matplotlib.pyplot as plt

# ------------------------ PARAMETERS -----------------------------------------
# Unit cell dimensions and grid size
unit_cell_length = 4  # Length of the unit cell in the x and y directions
grid_size_x = 5       # Number of unit cells along the x-axis
grid_size_y = 5       # Number of unit cells along the y-axis

# Total dimensions of the lattice
lattice_length_x = grid_size_x * unit_cell_length
lattice_length_y = grid_size_y * unit_cell_length

# Energy levels for different site types
site_energy_levels = [-0.79894, -0.79894]  # Example energies for site types
num_site_types = len(site_energy_levels)

# Interaction energies between hydrogen atoms and the surface
# interaction_energies = [0.0625, 0.0202, 0.0161, 0.0131, 0.0061, 0.0077, -0.0172]
interaction_energies = [0.060728968634255566, 0.021656454628845037, 0.014815471617979198, 0.012432355215369258, 0.006358444158441091, 0.005580559734457011, -0.013997341101679505]
correlations = [
    np.array([[7,0,5,0,4,0,5,0,6],
              [0,0,0,0,0,0,0,0,0],
              [5,0,3,0,1,0,2,0,5],
              [0,0,0,0,0,0,0,0,0],
              [4,0,1,0,0,0,1,0,4],
              [0,0,0,0,0,0,0,0,0],
              [5,0,2,0,1,0,3,0,5],
              [0,0,0,0,0,0,0,0,0],
              [6,0,5,0,4,0,5,0,7]], dtype=int),
    np.array([[6,0,5,0,4,0,5,0,7],
              [0,0,0,0,0,0,0,0,0],
              [5,0,2,0,1,0,3,0,5],
              [0,0,0,0,0,0,0,0,0],
              [4,0,1,0,0,0,1,0,4],
              [0,0,0,0,0,0,0,0,0],
              [5,0,3,0,1,0,2,0,5],
              [0,0,0,0,0,0,0,0,0],
              [7,0,5,0,4,0,5,0,6]], dtype=int)
]
correlation_length = len(correlations[0])

# ------------------------ FUNCTIONS -----------------------------------------

def shift_coordinates(coordinates, vector):
    """
    Shifts a set of coordinates by a given vector.
    :param coordinates: List of coordinates to shift.
    :param vector: The vector by which to shift the coordinates.
    :return: List of shifted coordinates.
    """
    return [list(np.array(coord, dtype=int) + np.array(vector, dtype=int)) for coord in coordinates]

def generate_lattice(unit_cell, lattice_vector, num_cells_x, num_cells_y):
    """
    Generates a lattice by replicating a unit cell.
    :param unit_cell: Initial unit cell coordinates.
    :param lattice_vector: Vector defining the size of the unit cell.
    :param num_cells_x: Number of cells in the x-direction.
    :param num_cells_y: Number of cells in the y-direction.
    :return: Coordinates of the entire lattice.
    """
    lattice = unit_cell
    for i in range(1, num_cells_x):
        lattice += shift_coordinates(unit_cell, [0, lattice_vector[1] * i, 0])
    unit_cell_temp = lattice
    for i in range(1, num_cells_y):
        lattice += shift_coordinates(unit_cell_temp, [0, 0, lattice_vector[2] * i])
    return lattice

def pick_random(empty_positions):
    """
    Randomly picks a position from the list of empty positions.
    :param empty_positions: List of available empty positions.
    :return: Chosen position and updated list of empty positions.
    """
    chosen_position = empty_positions.pop(rd.randrange(0, len(empty_positions), 1))
    return chosen_position, empty_positions

def update_flag_matrix(flag_matrix, h_position, value):
    """
    Updates the flag matrix to mark hydrogen presence.
    :param flag_matrix: The current flag matrix.
    :param h_position: Position of the hydrogen atom.
    :param value: Value to set in the flag matrix (1 for present, 0 for absent).
    :return: Updated flag matrix.
    """
    for i in range(3):
        for ii in range(3):
            flag_matrix[lattice_length_x * i + lattice_length_x - 1 - h_position[2], lattice_length_x * ii + h_position[1]] = value
    return flag_matrix

def add_hydrogen_randomly(H_positions, flag_matrix, empty_positions):
    """
    Adds a hydrogen atom randomly on the lattice.
    :param H_positions: List of current hydrogen positions.
    :param flag_matrix: The current flag matrix.
    :param empty_positions: List of available empty positions.
    :return: Updated hydrogen positions, flag matrix, and empty positions.
    """
    h_position, empty_positions = pick_random(empty_positions)
    H_positions.append(h_position)
    flag_matrix = update_flag_matrix(flag_matrix, h_position, 1)
    return H_positions, flag_matrix, empty_positions

def add_hydrogen_near_origin(H_positions, flag_matrix, empty_positions, origin_position):
    """
    Adds a hydrogen atom near a specified origin position, simulating Kawasaki dynamics.
    :param H_positions: List of current hydrogen positions.
    :param flag_matrix: The current flag matrix.
    :param empty_positions: List of available empty positions.
    :param origin_position: The position around which to add hydrogen.
    :return: Updated hydrogen positions, flag matrix, and empty positions.
    """
    nearby_positions = [[0, -2, -2], [0, 2, 2], [0, -2, 2], [0, 2, -2],
                        [-1, 0, 2], [-1, 2, 0], [-1, 0, -2], [-1, -2, 0], [0, 0, 0]]
    rd.shuffle(nearby_positions)
    for vector in nearby_positions:
        candidate_position = [
            abs(origin_position[0] + vector[0]),
            (origin_position[1] + vector[1]) % lattice_length_x,
            (origin_position[2] + vector[2]) % lattice_length_y
        ]
        if candidate_position in empty_positions:
            H_positions.append(candidate_position)
            flag_matrix = update_flag_matrix(flag_matrix, candidate_position, 1)
            empty_positions.remove(candidate_position)
            break
    return H_positions, flag_matrix, empty_positions

def remove_hydrogen(position_to_remove, H_positions, flag_matrix, empty_positions):
    """
    Removes a hydrogen atom from the lattice.
    :param position_to_remove: The position of the hydrogen atom to remove.
    :param H_positions: List of current hydrogen positions.
    :param flag_matrix: The current flag matrix.
    :param empty_positions: List of available empty positions.
    :return: Updated hydrogen positions, flag matrix, and empty positions.
    """
    H_positions.remove(position_to_remove)
    empty_positions.append(position_to_remove)
    flag_matrix = update_flag_matrix(flag_matrix, position_to_remove, 0)
    return H_positions, flag_matrix, empty_positions

def calculate_energy(H_position, flag_matrix):
    """
    Calculates the interaction energy of a hydrogen atom at a given position.
    :param H_position: The position of the hydrogen atom.
    :param flag_matrix: The current flag matrix.
    :return: Number of interactions per type, interaction energy contributions, total energy.
    """
    interaction_area = flag_matrix[2 * lattice_length_y - 1 - H_position[2] - int((correlation_length - 1) / 2):
                                    2 * lattice_length_y - 1 - H_position[2] + int((correlation_length - 1) / 2) + 1,
                                    lattice_length_x + H_position[1] - int((correlation_length - 1) / 2):
                                    lattice_length_x + H_position[1] + int((correlation_length - 1) / 2) + 1] * \
                       correlations[H_position[0]]
    
    num_interactions_per_type = np.bincount(interaction_area.ravel(), minlength=len(interaction_energies) + 1)[1:]
    interaction_energy = np.sum(num_interactions_per_type * interaction_energies)
    total_energy = interaction_energy + site_energy_levels[H_position[0]]
    return num_interactions_per_type, interaction_energy, total_energy

def plot_energy_convergence(total_steps, energy_values, current_H, max_H):
    """
    Plots the energy convergence over simulation steps.
    :param total_steps: Total number of Monte Carlo steps.
    :param energy_values: List of energy values at each step.
    :param current_H: Current number of hydrogen atoms.
    :param max_H: Maximum possible number of hydrogen atoms.
    """
    plt.plot(range(1, total_steps + 1), energy_values)
    plt.xlabel('MC Step')
    plt.ylabel('Energy (eV)')
    plt.title(f'{current_H}/{max_H} ML Coverage')
    plt.show()
