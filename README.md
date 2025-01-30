

In Development: Note that this code is still a work in progress. I am cleaning it up to make it more readable by people other than myself.


<ins>Intorduction</ins>
Resonant dispersive wave generation is a technique which has been recently applied to hollow capillary fibres. It allows for the generation of high pulse energy ultrashort laser pulses of < 5 fs at previously very difficult to reach wavelengths . It involves sending a pump pulse at a longer wavelength into a hollow capillary fibre filled with a noble gas. The nonlinear dynamics that occur when the pump pulse interacts with the medium can lead to the generation of a near transform limited laser pulse at a much shorter wavelength. However, due to the inherently nonlinear nature of the dynamics that occur in this system, it is very difficult to predict analytically what system parameters are required to generate the optimal RDW (optimal is defined here as highest peak power, close to gaussian temporal pulse shape and a pulse duration of < 5fs). This is a stumbling block for researchers who are trying to implement a RDW generation system in their lab. How do they figure out what fibre and pulse parameters to use to generate their optimal RDW for whatever laser system they have in their lab?

This is where optimisation algorithms come into play. These algorithms are designed to identify the values of a functions variables that maximise said function. Here we are using Bayesian optimisation (BO). Luna.jl is a open source code base written in Julia that allows for the simulation of nonlinear processes in hollow capillary fibres, which includes RDW generation. Therefore by combining BO with Luna.jl we can let the optimisation algorithm determine what the system parameters are for generating the optimal RDW. 

<ins>Experimental Overview</ins>
We have a fused silica hollow capillary fibre with radius r (usually<500 micrometer), length L (less than a few m) and filled with a noble gas at pressure P (less than 10 bar). The pump pulse has a pulse energy E (usually less than a few mJ) and a pulse duration T (<30 fs) and a central wavlelength λ. The pump pulse has a Gaussian spectrum and is transform limited. Note the values in brackets are only order of magnitude and vary heavily depending on the pump pulse and the RDW that is desired. They work best for a 800 nm pump wavelength trying to achieve a RDW at 200 nm.  All of these variables are called the system parameters. If the system parameters are chosen well we can generate a RDW at a central wavlength λ_RDW. I will not be covering the details of the underlying physics here. If you are interested there is extensive literature on the subject. Here is a link to a review paper https://doi.org/10.1063/5.0206108. 

Note that the code as is is set up to optimise the RDW at a central wavelengh of 200 nm when driving with a pump pulse of 800 nm central wavelength. You need to edit the vital_func_for_optimisation.py file if you want to target other RDW wavelengths or pump with different pump wavelengths.

<ins>Code Quickstart</ins>
The below is the BO.py file. The vital_func_for_optimisation.py needs to be in the same directory as BO.py if not added to PATH.
```
from vital_func_for_optimisation import BO
pbounds = {
    'peakpower': (0.05, 0.4),
    'duration': (5e-15, 35e-15),
    'pressure': (0.5, 5),
    'flength': (0.25, 5)}  

init_points = 20
n_iter = 250
random_state_list = [22000]

folder_path = r
file_name = r
Summary_folder_path = r
Summary_file_name = r

for state in random_state_list:
    BO(pbounds,init_points, n_iter, state,folder_path, file_name, Summary_folder_path, Summary_file_name)

```
This code works by having the BO algorithm decide on a given set of system parameters values, send them to Luna.jl where a simulation with those parameter values is run. The Luna.jl then evaluates the objective function (OF), which is the function that BO is trying to maximise. In this case this is the peak power of the RDW. The OF value is then sent back to the BO algorithm, which, with this new data decides on which next set of system parameter values to probe. This continues until the allocated number of allowed simulation runs is exhausted. At that point the BO algorithm sends you the OF value that was largest out of all the points probed. Note that (n_init) of the allowe simulation runs are used to essetnially probe random sets of system parameter values to essentially get some training data. Then (n_iter) number of simulation runs are done where the algorithm is actually trying to maximise the OF. I would set () to 20 and () to 200. This makes the code run in around 12 hours.

Now to discuss the system paremetsr.We fix the fibre radius r (units m) to a certain value. You can think of your radius as setting the "scale" of your system, in the sense that the bigger you make r the more pump pulse energy you need and the longer the fiber will be. This is a very approximate explanation. For more detail please see the published paper on the topic. The OF variables are T(seconds),P(bar),L (m) and P_pump. P_pump_scaled is the peak power of the pump pulse but expressed as a ratio to the critical power for self-focusing P_crit. So P_pump_scaled=P_pump/P_crit. P_crit is the peak power of a laser pulse necceary to initiate self-focusing in the noble gas that fills the fiber. P_pump_scaled varies from 0-1. For why again read the published paper on this topic. 

pbounds is the dictionary that contains the system parameters names and ranges. random_state_list is a list of random seeds. Each random seed is used to generate the random training data (n_init). The BO algorithm will be run for each entry in the random_state_list. 

folder_path is the path to the folder where you want all the results of the optimisation data saved. If on windows just right click on folder and click "Copy as path" in File explorer. file_name is the name of the csv file that contains all the points probed by the BO algorithm. Summary_folder_path is the path to a seperate folder. Summary_file_name is name of csv file saved in that folder. It summarises the system parameter values that are optimum identified by the BO indexed by the random_state used as the seed to determine the training data, as well as the RDW peak power that is associated with those values. Note that there are two RDW peak powers. The "raw" one refers to the peak power given by the faster but slightly inaccurate simulations run by Luna.jl when it is being called by BO (to speed up runtime). After the BO algorithm is finished an the opimum identified, it will run a more accurate "check" simulation using the optimum parameter values, which is also dispalyed in this csv as the "checked" RDW peak power. For more details on this refer to the published paper on this. 



<ins>Details on vital_func_for_optimisation.py: </ins>

IMPORTANT! If you are wanting to pump your system with a pump pulse that has a central wavelength that is different than 800 nm you need to edit the appropirate variable in vital_func_for_optimisation.py. Its called input_wavelength and is in m (so 800 nm is 800e-9). Similarly if you want to optimise for a different radius you need to change the radius variable (in m so 75 micrometer is 75e-6). Also if you want to use a different gas than Helium you need to change the gas variable to either Ar (Argon), Ne (Neon). 

If you want to change the RDW wavelength that you are targeting for optimisation, things get a bit trickier. The code calls a function called Processing.peakpower in the taret_func. This takes the simulated data generated by Luna.jl and evaluates the peakpower of the pulse exiting the fiber after filtering out any wavelength that is outside the bandpass range. This can be controlled by altering the variable xxx, which contains the lower and the upper wavlength of your bandpass in m (soo 185 nm is 185e-9). The center of this bandpass range is the central wavelength of the RDW that you are generating.

When the RDW is produced it is co-propagating with the pump pulse. This means we need some sort of dichoric mirror (usually a multi-layer coated dielectric mirror), that preferentially refelcts the RDW but transmits the pump pulse. These mirrors have a range of wavelengths over which they have very good reflection. This range of wavelengths is what determines your bandpass range mentioned above. 

Lastly. The target_func and the check_function are what actually call the Luna.jl simulation. They have a λlims variable in the prop_capillary function, which controls which wavelengths are allowed to exist in the simulation. If this is lowered below 100 nm then simulations in Argon fail as there is some problem with the physical parameters for Argon at this wavelength. For more details on the Luna.jl simulation please check out their Github (link below).



<ins>Installation: </ins>
Due to Luna.jl being written in Julia, and the BO algorithm in Python we have to make it so that a python code can run a Julia code and extract the produced data for analysis.

Luna plus BO Code Installation Guide 
1.	First install anaconda. Install the latest anaconda distribution from https://www.anaconda.com/download/success
2.	Do just me, and note destination folder (currently: C:\Users\tk716\AppData\Local\anaconda3)
3.	Add anaconda to my PATH variable

Then install Julia.
1.	Go to https://julialang.org/downloads/ and download the correct installer.  
2.	Run the installer , add to path, note the install location ("C:\Users\tk716\AppData\Local\Programs\Julia-1.11.3" currently)
3.	Once this is finished open the Julia command line via the appropriate short cut or by typing Julia in command prompt 
4.	Then write the following commands and press enter.This will establish a connection between jupyter notebook and Julia. 
using Pkg 
Pkg.add("IJulia") 
 
5.	If you now launch jupyter notebook and click “New”, the dropdown menu will give you the option to launch a notebook running a Julia kernel. 
6.	To install Luna, again open the Julia Command line. Enter the following commands and press enter 
using Pkg 
Pkg.add("Luna") 
7.	This will have successfully installed the Luna simulation. 
Making Python be able to Julia code
Python and Julia are two separate programming languages. However people have written code to allow one to run code in the other and then extract the data. We need to be able to make python

1.	Install PyCall by running in the Julia REPL: 
using Pkg
Pkg.add("PyCall")
2.	check it is using the Python interpreter desired:

using PyCall
PyCall.python

3.	If the desired interpreter is anaconda, you can double check by importing a module that comes preinstalled
using PyCall
pd = pyimport("pandas")

4.	If 3. Doesn’t work then you can set  the desired interpreter, run:
using Pkg
ENV["PYTHON"] = raw"C:\Users\mmm120\AppData\Local\anaconda3\python.exe"
Pkg.build("PyCall")

Check again the interpreter (two steps above), can also check that loads pandas.

To exit the package manager (entered by typing  ]  , one can return to Julia by typing the same bracket again or by pressing the delete key.

If when trying to run Julia code in Python (eg: Spyder), and the following error pops up:
In Julia >= 0.7, above two paths to `libpython` have to match exactly 
in order for PyJulia to work out-of-the-box.  To configure PyCall.jl to use 
Python interpreter "C:\Users\mmm120\AppData\Local\anaconda3\python.exe", 
run the following code in the Python REPL: 

import julia 
julia.install() 
For more information, see: 
    https://pyjulia.readthedocs.io/en/latest/troubleshooting.html 

Run the indicated code in the python repl and will be solved.

If ”UnsupportedPythonError: It seems your Julia and PyJulia setup are not supported” and points to Pycall and python having different interpreters, the pycall interpreter may have changed. 
To check which interpreter it is using, run in Julia’s REPL: 
using PyCall 
PyCall.python 

If it is not the anaconda python installation, change the path to your anaconda python installation (running in the PC command line: where python)
using Pkg
ENV["PYTHON"] = raw"C:\Users\RDcam\anaconda3\python.exe"
Pkg.build("PyCall")

BO
Finally, install Bayesian Optimisation, by running in the anaconda prompt command line:
conda install conda-forge::bayesian-optimization.

As well as the SMT package:
conda install conda-forge::smt








<ins>Dependencies:</ins>
Open source library for Bayesian Optimisation in python: (https://github.com/bayesian-optimization/BayesianOptimization)

Luna.jl (written in Julia) for simulating nonlinear dynamics in gas filled hollow capillary fibres. (https://github.com/LupoLab/Luna.jl)
 
BO calls the Luna.jl simulations. Uses pyJulia to let the two communicate (https://github.com/JuliaPy/pyjulia).
