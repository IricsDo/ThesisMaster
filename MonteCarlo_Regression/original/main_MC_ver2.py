# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 15:44:20 2021

@author: Nguyen Van Hoa
"""

#------------------------PARAMETERS-----------------------------------------

import module_ver2 as md
import numpy as np
import random as rd
import math
import time 
import pandas as pd
from joblib import Parallel, delayed

kB= 8.6173324*10**(-5) #(eV/T)

a=4 #lenght of pt(100)-(1x1) unit cell
b=2
c=1
h=b
k=c
T=303  #[0.0261] temperature
nequiv=10000
nmeasure=10e6 # 10e6
n_x=5
n_y=5
len_x = n_x*a
len_y = n_y*a

kBT=kB*T

label = ['Temp','Loading','Ave Eng','Accept Rate','Vint1','Vint2','Vint3','Vint4','Vint5','Vint6','Vint7','runtime']#,'Vint6','Vint7'

ntot=int(nequiv+nmeasure)
h_unit_site = [[0,1,1],[0,3,3],[1,3,1],[1,1,3]] #only including sb sites

lattice_vector = [0,a,a]
empty_pos = md.lattice(h_unit_site,lattice_vector,n_x,n_y)
flag=np.zeros([3*(n_x)*a,3*(n_y)*a], dtype=int)

max_H=n_x*n_y*len(h_unit_site)

E_site=[-0.79894,-0.79894] #sb1, sb2

#E_int=[0.06328,0.02800,0.00717,0.00951,0.01052]
#E_int=[0.06082,0.02800,0.00970,0.01300,0.00956,-0.00024,-0.01200]
# E_int=[999,0.02814,0.00676,0.00964,0.01295] # 5 int
E_int=[0.062496199361503475,	0.020194447685764472, 0.016086159610678434, 0.013118399928951235, 0.006094621115936579,	0.007694570521806183, -0.017156967355965367]

#_____________________________________________________________________

def calculate_at_numH(num_H):
    start_time = time.time()
    accept_rate = 0
    sum_energy = 0
    E_corr = [0]*len(E_int)
    rate = 0
    #sb = 0
    #f = 0
    #t = 0
    empty_pos = md.lattice(h_unit_site,lattice_vector,n_x,n_y)
    flag=np.zeros([3*(n_x)*a,3*(n_y)*a], dtype=int)
    H_pos=[] #clear all H adsorbed
    while len(H_pos) < num_H:
        H_pos,flag,empty_pos = md.add_H_1(H_pos,flag,empty_pos)
    
    #calculating initial energy
    E_corr_last=np.zeros(len(E_int),dtype=float)
    energy_last=0
    for i in H_pos:
        num_type,E_int_h,energy_h = md.energy_H(i, flag)
        E_corr_last += E_int_h*0.5
        energy_last += energy_h
    energy_last = energy_last - sum(E_corr_last)
    if E_corr_last[0]!=0:
        print(E_corr_last[0])
    
    #---------------MC loop: shifting hydro to another pos ---------------
    for i in range(0,ntot):    
    #creating recovery point
        H_pos_temp = list(H_pos)
        flag_temp = np.array(flag,dtype=int)
        empty_pos_temp = list(empty_pos)
        energy_last_temp = energy_last
        E_corr_last_temp = np.array(E_corr_last,dtype=float)
        
    #shifting hydro = deleting hydro + adding hydro    
        #delete 1 hydro and calculate the energy that hydro contributing to the system
        h_moved = H_pos[rd.randrange(0,num_H,1)]
        
        num_type,E_int_moved,E_h_moved = md.energy_H(h_moved,flag)
        E_corr_check = E_corr_last - E_int_moved
        energy_check = energy_last - E_h_moved
        
        H_pos,flag,empty_pos = md.del_H(h_moved,H_pos,flag,empty_pos)
        
        #add 1 hydro and calculate the energy that hydro contributing to the system
        H_pos,flag,empty_pos = md.add_H_1(H_pos,flag,empty_pos)
        #H_pos,flag,empty_pos = md.add_H_2(H_pos,flag,empty_pos,h_moved)
        num_type,E_int_added,E_h_added = md.energy_H(H_pos[-1],flag)
        E_corr_check = E_corr_check + E_int_added
        energy_check = energy_check + E_h_added
        
        #checking
        if energy_check <= energy_last:
            E_corr_last=np.array(E_corr_check,dtype=float)
            energy_last=energy_check
            rate=1
        else:
            wt = math.exp((energy_last-energy_check)/(kBT)) #Boltzmann
            r=rd.random()
            if r<=wt: #accepted 
                E_corr_last=np.array(E_corr_check,dtype=float)
                energy_last=energy_check
                rate=1
            else:                           #reject, return the old H site
                H_pos = list(H_pos_temp)
                empty_pos = list(empty_pos_temp)
                flag = np.array(flag_temp,dtype=int)
                energy_last = energy_last_temp
                E_corr_last = np.array(E_corr_last_temp,dtype=float)
                rate=0
        #print(rate, energy_last,E_corr_last)       
    #calculating mean values
        if i > (nequiv-1):
            accept_rate += rate
            sum_energy += energy_last
            E_corr += E_corr_last
            if energy_last > 0:
                print(T, num_H,'need to be re-run!')
                break
    
    #printing time collapse
    end_time=time.time()
    print(T, num_H, end_time - start_time)    
    
    #result table
    temp=[T, num_H, sum_energy/nmeasure, accept_rate/nmeasure]
    for i in range(0, len(E_corr)):
        temp.append(E_corr[i]/nmeasure)
    temp.append(end_time - start_time)
    
    temp=np.array(temp)
    df = pd.DataFrame(np.reshape(temp, (1,5+len(E_int))))
    df.to_csv(fol_name,mode='a',index=None, header=None)

#------------------------------------------------------------------------------
    
fol_name=str(n_x)+'x'+str(n_y)+'_'+str(T)+'_MD_'+str(nmeasure)+'testing.csv'
temp=np.zeros(shape=(1,len(E_int)+5),dtype=int)
df = pd.DataFrame(temp)
df.to_csv(fol_name,header=label,index=False)        
    
Parallel(n_jobs=1)(delayed(calculate_at_numH)(num_H) for num_H in range(1,51))           