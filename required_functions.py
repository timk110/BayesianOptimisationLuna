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
from bayes_opt import acquisition


julia_path="C:\\Users\\tk716\\AppData\\Local\\Programs\\Julia-1.9.2\\bin\\julia.exe"
julia.Julia(runtime=julia_path)

input_wavelength=800e-9
radius=75e-6
gas="He"
wavelength_filter=(185e-9,215e-9)
def target_func(peakpower,duration,pressure,flength):
    

    
    
    Main.using("Luna")
    Main.gas_str =gas
    Main.eval("gas = Symbol(gas_str)")
    Main.λ0=input_wavelength
    Main.radius=radius
    
    Main.pressure=pressure
    n_n2=Main.eval("Tools.getN0n0n2((2*pi*3e8)/λ0,gas;P=pressure)")
    Pcrit=(0.148*(input_wavelength)**2)/(n_n2[1]*n_n2[2])
    peakpower_realunits=Pcrit*peakpower
    energy=(duration*peakpower_realunits)/0.94
    
    Main.energy=energy
    Main.τfwhm = duration
    Main.flength=flength
 
    
    Main.wavelength_filter=wavelength_filter
    Main.duv = Main.eval('duv = prop_capillary(radius, flength, gas, (pressure,0); λ0 ,modes=3,τfwhm, energy ,trange=1000e-15, λlims=(100e-9, 3e-6))')
    peak_power_list=Main.eval("Processing.peakpower(duv,flength,bandpass=wavelength_filter)")
    
    return peak_power_list[0][0]


    
def check_func(peakpower,duration,pressure,flength):

    
    Main.using("Luna")
    Main.gas_str =gas
    Main.eval("gas = Symbol(gas_str)")
    Main.λ0=input_wavelength
    Main.radius=radius
    
    Main.pressure=pressure
    n_n2=Main.eval("Tools.getN0n0n2((2*pi*3e8)/λ0,gas;P=pressure)")
    Pcrit=(0.148*(input_wavelength)**2)/(n_n2[1]*n_n2[2])
    peakpower_realunits=Pcrit*peakpower
    energy=(duration*peakpower_realunits)/0.94
    
    Main.energy=energy
    Main.τfwhm = duration
    Main.flength=flength
 
    
    Main.wavelength_filter=wavelength_filter
    
    Main.duv = Main.eval('duv = prop_capillary(radius, flength, gas, (pressure,0); λ0 ,modes=7,τfwhm, energy ,trange=2000e-15, λlims=(100e-9, 4e-6))')

    peak_power_list=Main.eval("Processing.peakpower(duv,flength,bandpass=wavelength_filter)")
    
    return peak_power_list[0][0]

def BO(pbounds,kappa,init_points,n_iter,random_state,folder_path,file_name,Summary_folder_path,Summary_file_name):


    acquisition_function = acquisition.UpperConfidenceBound(kappa=kappa)

    optimizer = BayesianOptimization(
        f=target_func,
        acquisition_function=acquisition_function,
        pbounds=pbounds,
        random_state=random_state,allow_duplicate_points=True)
        
    
    
    
   
    
    
    
    start=time.time()
    optimizer.maximize(init_points,n_iter)
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
    
    
    full_file_name="k"+str(kappa)+"-"+str(init_points)+"-"+str(n_iter)+"-rs"+str(random_state)+file_name
    # Concatenate the folder path and file name
    full_path = f'{folder_path}/{full_file_name}'
    
    # Save the DataFrame to CSV in the specified folder
    df.to_csv(full_path, index=False)
   
    # Concatenate the folder path and file name
    Summary_full_path = f'{Summary_folder_path}/{Summary_file_name}'
    
    new_summary_data=pd.DataFrame({"Aquisition Function":["UCB"],"Random State":[random_state],"Kappa":[kappa],"No of Initial Points":[init_points],"Max Number of Iterations":[n_iter],"Runtime":[finish],"Optima Duration /s":[optimizer.max["params"]["duration"]],"Optima Fibre Length /m":[optimizer.max["params"]["flength"]],"Optima Pump Peak Power /Pcrit":[optimizer.max["params"]["peakpower"]],"Optima Pressure /bar":[optimizer.max["params"]["pressure"]],"Optima RDW peak power raw":[optimizer.max["target"]],"Optima RDW peak power checked":[checked_RDW_peak_power_HE11]})

    
    

    if any(filename.endswith(".csv") for filename in os.listdir(Summary_folder_path)):
        summary=pd.read_csv(Summary_full_path)

        updated_summary = pd.concat([summary,new_summary_data ], ignore_index=True)

        updated_summary.to_csv(Summary_full_path, index=False)
    
    else:
        empty_summary=pd.DataFrame({"Aquisition Function":[],"Random State":[],"Kappa":[],"No of Initial Points":[],"Max Number of Iterations":[],"Runtime":[],"Optima Duration /s":[],"Optima Fibre Length /m":[],"Optima Pump Peak Power /Pcrit":[],"Optima Pressure /bar":[],"Optima RDW peak power raw":[],"Optima RDW peak power checked":[]})
        updated_summary = pd.concat([empty_summary,new_summary_data ], ignore_index=True)
        updated_summary.to_csv(Summary_full_path, index=False)
    return
 




