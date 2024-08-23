# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 15:06:43 2021

@author: Nguyen Van Hoa

flag: np.array() size 4*(N+2) x 4*(N+2), marking the presentation sites of H
    : N+2 presented periodic condition
"""


#------------------------PARAMETERS-----------------------------------------
import numpy as np
import random as rd
import matplotlib.pyplot as plt
a=4 #lenght of pt(100)-(1x1) unit cell
b=2
c=1
h=b
k=c
n_x=5
n_y=5
len_x=n_x*a
len_y=n_y*a

E_site=[-0.79894,-0.79894] #sb1, sb2

type_site=len(E_site)

corr=list(range(0,type_site))

'''
#E_int=[0.06082,0.02800,0.00970,0.01300,0.00956,-0.00024,-0.01200]
E_int=[0.06122,	0.02592, 0.01089, 0.01323, 0.00913,	0.00200, -0.01219]

corr[0]=np.array([[7,0,5,0,4,0,5,0,6],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 5,0,3,0,1,0,2,0,5],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 4,0,1,0,0,0,1,0,4],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 5,0,2,0,1,0,3,0,5],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 6,0,5,0,4,0,5,0,7]],dtype=int)

corr[1]=np.array([[6,0,5,0,4,0,5,0,7],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 5,0,2,0,1,0,3,0,5],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 4,0,1,0,0,0,1,0,4],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 5,0,3,0,1,0,2,0,5],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 7,0,5,0,4,0,5,0,6]],dtype=int)

'''
# E_int=[999,0.02814,0.00676,0.00964,0.01295] # 5 int
# corr[0]=np.array([[0,0,5,0,4,0,5,0,0],\
#                  [ 0,0,0,0,0,0,0,0,0],\
#                  [ 5,0,3,0,1,0,2,0,5],\
#                  [ 0,0,0,0,0,0,0,0,0],\
#                  [ 4,0,1,0,0,0,1,0,4],\
#                  [ 0,0,0,0,0,0,0,0,0],\
#                  [ 5,0,2,0,1,0,3,0,5],\
#                  [ 0,0,0,0,0,0,0,0,0],\
#                  [ 0,0,5,0,4,0,5,0,0]],dtype=int)

# corr[1]=np.array([[0,0,5,0,4,0,5,0,0],\
#                  [ 0,0,0,0,0,0,0,0,0],\
#                  [ 5,0,2,0,1,0,3,0,5],\
#                  [ 0,0,0,0,0,0,0,0,0],\
#                  [ 4,0,1,0,0,0,1,0,4],\
#                  [ 0,0,0,0,0,0,0,0,0],\
#                  [ 5,0,3,0,1,0,2,0,5],\
#                  [ 0,0,0,0,0,0,0,0,0],\
#                  [ 0,0,5,0,4,0,5,0,0]],dtype=int)

''' 
E_int=[0.06328,0.02800,0.00717]
corr[0]=np.array([[3,0,1,0,2],\
                 [ 0,0,0,0,0],\
                 [ 1,0,0,0,1],\
                 [ 0,0,0,0,0],\
                 [ 2,0,1,0,3]],dtype=int)

corr[1]=np.array([[2,0,1,0,3],\
                 [ 0,0,0,0,0],\
                 [ 1,0,0,0,1],\
                 [ 0,0,0,0,0],\
                 [ 3,0,1,0,2]],dtype=int)
'''
E_int=[0.062496199361503475,	0.020194447685764472, 0.016086159610678434, 0.013118399928951235, 0.006094621115936579,	0.007694570521806183, -0.017156967355965367]
corr[0]=np.array([[7,0,5,0,4,0,5,0,6],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 5,0,3,0,1,0,2,0,5],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 4,0,1,0,0,0,1,0,4],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 5,0,2,0,1,0,3,0,5],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 6,0,5,0,4,0,5,0,7]],dtype=int)

corr[1]=np.array([[6,0,5,0,4,0,5,0,7],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 5,0,2,0,1,0,3,0,5],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 4,0,1,0,0,0,1,0,4],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 5,0,3,0,1,0,2,0,5],\
                 [ 0,0,0,0,0,0,0,0,0],\
                 [ 7,0,5,0,4,0,5,0,6]],dtype=int)
L=len(corr[0])
#___________________________________________________________________________

def shift(configure,vector): ##vector=[x,y]
    shifted_config=[]
    for coor in configure:
        shifted_config.append(list(np.array(coor,dtype=int)+np.array(vector,dtype=int)))
    return shifted_config

def lattice(unit_cell, lattice_vector, n_x, n_y): #characterized by label h site 0,1 (sb1,sb2)
    lattice=unit_cell
    for i in range(1,n_x):
        lattice=lattice + shift(unit_cell,[0,lattice_vector[1]*i,0])
    unit_cell_temp=lattice
    for i in range(1,n_y):
        lattice=lattice + shift(unit_cell_temp,[0,0,lattice_vector[2]*i])
    return lattice

def pick_randow(empty_pos):
    chosen_pos=empty_pos[rd.randrange(0,len(empty_pos),1)]
    empty_pos.remove(chosen_pos)
    return chosen_pos,empty_pos

def flag_1(flag,h_pos,value):
    for i in range(3):
        for ii in range(3):
            flag[len_x*i+len_x-1-h_pos[2],len_x*ii+h_pos[1]]=value
    return flag

def add_H_1(H_pos,flag,empty_pos): #random
    h_pos, b= pick_randow(empty_pos)
    H_pos.append(h_pos)
    empty_pos=b
    flag=flag_1(flag,h_pos,1)
    return H_pos,flag,empty_pos

                                              #origin_pos must exist in empty_pos 
def add_H_2(H_pos,flag,empty_pos,origin_pos): #add H with Kawasaki dynamic type
    around_pos=[[0,-2,-2],[0,2,2],[0,-2,2],[0,2,-2],[-1,0,2],[-1,2,0],[-1,0,-2],[-1,-2,0],[0,0,0]]
    rd.shuffle(around_pos)
    for i in around_pos:
        chosen_pos=[abs(origin_pos[0]+i[0]),(origin_pos[1]+i[1])%len_x,(origin_pos[2]+i[2])%len_y]
        if empty_pos.count(chosen_pos)==1:
            H_pos.append(chosen_pos)
            flag=flag_1(flag,chosen_pos,1)
            empty_pos.remove(chosen_pos)
            break
        else: 
            continue
    return H_pos,flag,empty_pos

def del_H(present_H_pos, H_pos,flag, empty_pos):
    H_pos.remove(present_H_pos)
    empty_pos.append(present_H_pos)
    flag=flag_1(flag,present_H_pos,0)
    return H_pos,flag,empty_pos

def energy_H(h_pos, flag):
    temp=np.reshape(flag[2*len_y-1-h_pos[2]-int((L-1)/2):2*len_y-1-h_pos[2]+int((L-1)/2)+1,\
              len_x+h_pos[1]-int((L-1)/2):len_x+h_pos[1]+int((L-1)/2)+1]\
              *corr[h_pos[0]],L**2)
    temp=temp.tolist()
    num_type=[int(temp.count(i)) for i in range(1,len(E_int)+1)]
    E_int_h=np.multiply(num_type,E_int,dtype=float)
    energy_h=np.nansum(E_int_h)+E_site[h_pos[0]]
    return num_type,E_int_h,energy_h

def plot_Econv(ntot,E,num_H,max_H):  
    plt.plot(list(range(1,ntot+1)), E)
    plt.xlabel('MC_step')
    plt.ylabel('E(ev)')
    plt.title(str(num_H)+'/'+str(max_H)+' ML')
    plt.show() 