# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 16:30:32 2024

@author: tk716
"""

from required_functions import BO

pbounds={'peakpower': (0.05, 0.4), 'duration': (5e-15, 30e-15),'pressure': (2, 6),'flength': (0.15, 3)} #the range of the parameters that the BO will be alterting to try and optimise the objective function

kappa=5 #the parameter that controls whether the acquisition function focuses on exploitation (small k) or exploration (large k)
init_points=20 #the number of random points that the algorithm initially samples in the search space. These are used to build an initial data set for the BO to work on
n_iter=200 #the number of points that the algorithm samples using the BO approach.
random_state_list=[1000,2000]#the random seed that is used to determine how the random points are distributed in the search space. for each entry the BO algorithm is run one.

folder_path=r #the path to the folder where the details of each run of the algorithm is saved as a csv file
file_name=r # the name of the csv files in the above folder


Summary_folder_path=r # the path to the folder where the summary of the optimum that each run of the algorithm is saved as a csv file
Summary_file_name=r #the name of the summary file

for state in random_state_list:
    BO(pbounds,kappa,init_points,n_iter,state,domain_reduction,folder_path,file_name,Summary_folder_path,Summary_file_name)
