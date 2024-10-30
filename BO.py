# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 16:30:32 2024

@author: tk716
"""

from vital_func_for_optimisationh012 import BO
#pbounds={'peakpower': (0.005, 0.4), 'duration': (5e-15, 35e-15),'pressure': (0.5, 5),'flength': (0.25, 5)}

pbounds={'peakpower': (0.05, 0.4), 'duration': (39.9e-15, 40.1e-15),'pressure': (2, 6),'flength': (0.15, 3)}#note for duration in order for the domain reduction to work we have to have the time coordinate in the range 0-5, so the cehck and target func have been altered 
#similarly for peakpower we have a 10x multiplier, for duration we have 1e-14 mulitpiler in the tareget and check function
kappa=5
init_points=4
n_iter=20
random_state_list=[1000]
domain_reduction=False
folder_path=r"C:\Users\tk716\OneDrive - Imperial College London\Optimiser Results\H012"
file_name=r"BO-200nm-0.4pcrit-CR-5MM.csv"


Summary_folder_path=r"C:\Users\tk716\OneDrive - Imperial College London\Optimiser Results\H012\Summary"
Summary_file_name=r"Summ_of_BO_res_200nm_0.4Pcrit_CR_5MM.csv"

for state in random_state_list:
    BO(pbounds,kappa,init_points,n_iter,state,domain_reduction,folder_path,file_name,Summary_folder_path,Summary_file_name)
