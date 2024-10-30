# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 14:35:20 2024

@author: tk716
"""

#the BO approach 4D
import time
import pandas as pd
import os 
import julia
from julia import Main
from bayes_opt import BayesianOptimization
from bayes_opt import UtilityFunction
from bayes_opt import SequentialDomainReductionTransformer

from smt.sampling_methods import LHS

julia_path="C:\\Users\\tk716\\AppData\\Local\\Programs\\Julia-1.9.2\\bin\\julia.exe"
julia.Julia(runtime=julia_path)

def target_func(peakpower,duration,pressure,flength):
    
    peakpower=peakpower#*0.1
    duration=duration#*1e-14
    
    
    Main.using("Luna")
    Main.gas_str = "He"
    Main.eval("gas = Symbol(gas_str)")
    Main.λ0=800e-9
    Main.radius=75e-6
    
    Main.pressure=pressure
    n_n2=Main.eval("Tools.getN0n0n2((2*pi*3e8)/λ0,gas;P=pressure)")
    Pcrit=(0.148*(800e-9)**2)/(n_n2[1]*n_n2[2])
    peakpower_realunits=Pcrit*peakpower
    energy=(duration*peakpower_realunits)/0.94
    
    Main.energy=energy
    Main.τfwhm = duration
    Main.flength=flength
 
    Main.duv = Main.eval('duv = prop_capillary(radius, flength, gas, (pressure,0); λ0 ,modes=3,τfwhm, energy ,trange=1000e-15, λlims=(100e-9, 3e-6))')
    peak_power_list=Main.eval("Processing.peakpower(duv,flength,bandpass=(185e-9,215e-9))")
    
    return peak_power_list[0][0]#[0] ensures we are looking at peak power in mode 1


    
def check_func(peakpower,duration,pressure,flength):
    peakpower=peakpower#*0.1
    duration=duration#*1e-14
    
    
    
    
    Main.using("Luna")
    Main.gas_str = "He"
    Main.eval("gas = Symbol(gas_str)")
    Main.λ0=800e-9
    Main.radius=75e-6
    
    Main.pressure=pressure
    n_n2=Main.eval("Tools.getN0n0n2((2*pi*3e8)/λ0,gas;P=pressure)")
    Pcrit=(0.148*(800e-9)**2)/(n_n2[1]*n_n2[2])
    peakpower_realunits=Pcrit*peakpower
    energy=(duration*peakpower_realunits)/0.94
    
    Main.energy=energy
    Main.τfwhm = duration
    Main.flength=flength
 
    
    Main.duv = Main.eval('duv = prop_capillary(radius, flength, gas, (pressure,0); λ0 ,modes=7,τfwhm, energy ,trange=2000e-15, λlims=(80e-9, 4e-6))')

    peak_power_list=Main.eval("Processing.peakpower(duv,flength,bandpass=(185e-9,215e-9))")
    Main.eval('Plotting.time_1D(duv,flength,bandpass=(185e-9,215e-9),modes=:sum)')
    Main.eval('Plotting.spec_1D(duv, flength,log10=false,modes=:sum)')

    
    
    return peak_power_list[0][0]#[0] ensures we are looking at peak power in mode 1

def BO(pbounds,kappa,init_points,n_iter,random_state,domain_reduction,folder_path,file_name,Summary_folder_path,Summary_file_name):

    # Bounded region of parameter space
    #pbounds = {'peakpower': (0.005, 0.4), 'duration': (5e-15, 35e-15),'pressure': (0.5, 5),'flength': (0.25, 5)}
    
    #the various variables that define the BO algorithm
    kind="ucb"
    #kappa=5
    #init_points=20
    #n_iter=250
    #random_state=12000
    
    if domain_reduction==True:
 
        bounds_transformer = SequentialDomainReductionTransformer(minimum_window=0.5)
        optimizer = BayesianOptimization(
            f=target_func,
            pbounds=pbounds,
            random_state=random_state,allow_duplicate_points=True,
            bounds_transformer=bounds_transformer)
    else:
        optimizer = BayesianOptimization(
            f=target_func,
            pbounds=pbounds,
            random_state=random_state,allow_duplicate_points=True)
        
    
    
    
    acquisition_function = UtilityFunction(kind=kind, kappa=kappa)
    
    
    
    start=time.time()
    optimizer.maximize(init_points,n_iter,acquisition_function=acquisition_function)
    finish=(time.time()-start)/60
    
    print("Runtime"+"="+str(finish)+"min")
    print(optimizer.max)
    
    
    pressure=optimizer.max["params"]["pressure"]
    peakpower=optimizer.max["params"]["peakpower"]
    duration=optimizer.max["params"]["duration"]
    flength=optimizer.max["params"]["flength"]
    

    
    checked_RDW_peak_power_HE11=check_func(peakpower,duration,pressure,flength)
    
    print("True RDW Peak Power is ="+str("{:e}".format(checked_RDW_peak_power_HE11))+"W")
    
    
    re_shuffled_list=[]
    for i in optimizer.res:
        params=i.get("params")
        re_shuffled_dict={"Peak_power":i.get("target")}
        re_shuffled_dict.update(params)
        re_shuffled_list.append(re_shuffled_dict)
    df=pd.DataFrame(re_shuffled_list)
    
    #folder_path = r"C:\Users\tk716\OneDrive - Imperial College London\0.4pcrit_short_BO_chrisrange"
    #file_name = r"BO-200nm-0.4pcrit-chrisrange-"+kind+"-k"+str(kappa)+"-"+str(init_points)+"-"+str(n_iter)+"-rs"+str(random_state)+"-MM.csv"
    full_file_name="DR"+str(domain_reduction)+"-"+kind+"-k"+str(kappa)+"-"+str(init_points)+"-"+str(n_iter)+"-rs"+str(random_state)+file_name
    # Concatenate the folder path and file name
    full_path = f'{folder_path}/{full_file_name}'
    
    # Save the DataFrame to CSV in the specified folder
    df.to_csv(full_path, index=False)
    
    #Summary_folder_path = r"C:\Users\tk716\OneDrive - Imperial College London\0.4pcrit_short_BO_chrisrange\summary"
    #Summary_file_name = r"Summary_of_BO_results_200nm_0.4Pcrit_chrisrange_3MM.csv"
    
    # Concatenate the folder path and file name
    Summary_full_path = f'{Summary_folder_path}/{Summary_file_name}'
    
    new_summary_data=pd.DataFrame({"Aquisition Function":[kind],"Random State":[random_state],"Kappa":[kappa],"No of Initial Points":[init_points],"Max Number of Iterations":[n_iter],"Runtime":[finish],"Optima Duration /s":[optimizer.max["params"]["duration"]],"Optima Fibre Length /m":[optimizer.max["params"]["flength"]],"Optima Pump Peak Power /Pcrit":[optimizer.max["params"]["peakpower"]],"Optima Pressure /bar":[optimizer.max["params"]["pressure"]],"Optima RDW peak power raw":[optimizer.max["target"]],"Optima RDW peak power checked":[checked_RDW_peak_power_HE11]})

    
    

    if any(filename.endswith(".csv") for filename in os.listdir(Summary_folder_path)):
        summary=pd.read_csv(Summary_full_path)

        updated_summary = pd.concat([summary,new_summary_data ], ignore_index=True)

        updated_summary.to_csv(Summary_full_path, index=False)
    
    else:
        empty_summary=pd.DataFrame({"Aquisition Function":[],"Random State":[],"Kappa":[],"No of Initial Points":[],"Max Number of Iterations":[],"Runtime":[],"Optima Duration /s":[],"Optima Fibre Length /m":[],"Optima Pump Peak Power /Pcrit":[],"Optima Pressure /bar":[],"Optima RDW peak power raw":[],"Optima RDW peak power checked":[]})
        updated_summary = pd.concat([empty_summary,new_summary_data ], ignore_index=True)
        updated_summary.to_csv(Summary_full_path, index=False)
    return
 

def maximin_LHC_func(ranges,n_fev,random_state,folder_path,file_name,Summary_folder_path,Summary_file_name):
    

    #ranges = np.array([[0.005,0.031],[5e-15,35e-15],[0.5,5],[0.25,0.5]])#bounds on the system paramters to be varied, note the order needs to be preserved

    #n_fev= 2#the number of function evaluations
    #random_state=3
    
    
    
    sampling = LHS(xlimits=ranges,criterion="maximin",random_state=random_state)#“maximin” or “m”: maximize the minimum distance between points, but place the point in a randomized location within its interval

    points_to_probe=sampling(n_fev)

    results={"peakpower":[],"duration":[],"pressure":[],"flength":[],"Peak_power":[]} #peakpower is the pump peak power, Peak_power is the RDW peak powert

    start=time.time()

    for point in points_to_probe:
        results["peakpower"].append(point[0])
        results["duration"].append(point[1])
        results["pressure"].append(point[2])
        results["flength"].append(point[3])
    
        RDW_peak_power_mode1=target_func(peakpower=point[0],duration=point[1],pressure=point[2],flength=point[3])
        results["Peak_power"].append(RDW_peak_power_mode1)

    finish=(time.time()-start)/60
    print(finish)
    
    #we now save the probed points to a csv 
    raw_data=pd.DataFrame(results)


    #folder_path = r"C:\Users\tk716\OneDrive - Imperial College London\Optimiser Results\brute force\0.4Pcrit Chris range\maximin_LHC"
    #file_name = r"MaximinLHC-200nm-0.31pcrit-chrisrange-"+str(n_fev)+"-"+"-rs"+str(random_state)+"-MM.csv"
    full_file_name="n_fev"+str(n_fev)+"-rs"+str(random_state)+"-"+file_name
    # Concatenate the folder path and file name
    full_path = f'{folder_path}/{full_file_name}'

    # Save the DataFrame to CSV in the specified folder
    raw_data.to_csv(full_path, index=False)


    

    #now we find the optima generated, check it using mor eaccurate simulation and save it to a seperate csv    
    max_RDWPeakPower_index = results["Peak_power"].index(max(results["Peak_power"]))

    optima_peakpower=results["peakpower"][max_RDWPeakPower_index]
    optima_duration=results["duration"][max_RDWPeakPower_index]
    optima_pressure=results["pressure"][max_RDWPeakPower_index]
    optima_flength=results["flength"][max_RDWPeakPower_index]
    optima_Peak_power_raw=results["Peak_power"][max_RDWPeakPower_index]

    optima_Peak_power_checked= check_func(optima_peakpower,optima_duration,optima_pressure,optima_flength)

    new_summary_data=pd.DataFrame({"Random State":[random_state],"No of Probed Points":[n_fev],"Runtime":[finish],"Optima Duration /s":[optima_duration],"Optima Fibre Length /m":[optima_flength],"Optima Pump Peak Power /Pcrit":[optima_peakpower],"Optima Pressure /bar":[optima_pressure],"Optima RDW peak power raw":[optima_Peak_power_raw],"Optima RDW peak power checked":[optima_Peak_power_checked]})
    


    #Summary_folder_path = r"C:\Users\tk716\OneDrive - Imperial College London\Optimiser Results\brute force\0.4Pcrit Chris range\maximin_LHC\summary"
    #Summary_file_name = r"Summary_of_maximinLHC_results_200nm_0.31Pcrit_chrisrange_3MM.csv"
    Summary_full_path = f'{Summary_folder_path}/{Summary_file_name}'



    if any(filename.endswith(".csv") for filename in os.listdir(Summary_folder_path)):
        summary=pd.read_csv(Summary_full_path)

        updated_summary = pd.concat([summary,new_summary_data ], ignore_index=True)

        updated_summary.to_csv(Summary_full_path, index=False)
    
    else:
        empty_summary=pd.DataFrame({"Random State":[],"No of Probed Points":[],"Runtime":[],"Optima Duration /s":[],"Optima Fibre Length /m":[],"Optima Pump Peak Power /Pcrit":[],"Optima Pressure /bar":[],"Optima RDW peak power raw":[],"Optima RDW peak power checked":[]})
        updated_summary = pd.concat([empty_summary,new_summary_data ], ignore_index=True)
    
        updated_summary.to_csv(Summary_full_path, index=False)
    return
 
    



