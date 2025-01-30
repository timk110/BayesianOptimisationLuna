

In Development: Note that this code is still a work in progress. I am cleaning it up to make it more readable by people other than myself.


<ins>Intorduction</ins>
Resonant dispersive wave generation is a technique which has been recently applied to hollow capillary fibres. It allows for the generation of high pulse energy ultrashort laser pulses of < 5 fs at previously very difficult to reach wavelengths . It involves sending a pump pulse at a longer wavelength into a hollow capillary fibre filled with a noble gas. The nonlinear dynamics that occur when the pump pulse interacts with the medium can lead to the generation of a near transform limited laser pulse at a much shorter wavelength. However, due to the inherently nonlinear nature of the dynamics that occur in this system, it is very difficult to predict analytically what system parameters are required to generate the optimal RDW (optimal is defined here as highest peak power, close to gaussian temporal pulse shape and a pulse duration of < 5fs). This is a stumbling block for researchers who are trying to implement a RDW generation system in their lab. How do they figure out what fibre and pulse parameters to use to generate their optimal RDW for whatever laser system they have in their lab?

This is where optimisation algorithms come into play. These algorithms are designed to identify the values of a functions variables that maximise said function. Here we are using Bayesian optimisation (BO). Luna.jl is a open source code base written in Julia that allows for the simulation of nonlinear processes in hollow capillary fibres, which includes RDW generation. Therefore by combining BO with Luna.jl we can let the optimisation algorithm determine what the system parameters are for generating the optimal RDW. 

<ins>Experimental Overview</ins>
We have a fused silica hollow capillary fibre with radius r (usually<500 micrometer), length L (less than a few m) and filled with a noble gas at pressure P (less than 10 bar). The pump pulse has a pulse energy E (usually less than a few mJ) and a pulse duration T (<30 fs) and a central wavlelength λ. Note the values in brackets are only order of magnitude and vary heavily depending on the pump pulse and the RDW that is desired.  All of these variables are called the system parameters. If the system parameters are chosen well we can generate a RDW at a central wavlength λ_RDW. I will not be covering the details of the underlying physics here. If you are interested there is extensive literature on the subject. Here is a link to a review paper https://doi.org/10.1063/5.0206108. 

<ins>Code Quickstart</ins>

This code works by having the BO algorithm decide on a given set of system parameters values, send them to Luna.jl where a simulation with those parameter values is run. The Luna.jl then evaluates the objective function (OF), which is the function that BO is trying to maximise. In this case this is the peak power of the RDW. The OF value is then sent back to the BO algorithm, which, with this new data decides on which next set of system parameter values to probe. This continues until the allocated number of allowed simulation runs is exhausted. At that point the BO algorithm sends you the OF value that was largest out of all the points probed. Note that () of the allowe simulation runs are used to essetnially probe random sets of system parameter values to essentially get some training data. Then () number of simulation runs are done where the algorithm is actually trying to maximise the OF. I would set () to 20 and () to 200. This makes the code run in around 12 hours.

Now to discuss the system paremetsr.We fix the fibre radius r to a certain value. You can think of your radius as setting the "scale" of your system, in the sense that the bigger you make r the more pump pulse energy you need and the longer the fiber will be. This is a very approximate explanation. For more detail please see the published paper on the topic. The OF variables are T,P,L and P_pump. P_pump_scaled is the peak power of the pump pulse but expressed as a ratio to the critical power for self-focusing P_crit. So P_pump_scaled=P_pump/P_crit. P_crit is the peak power of a laser pulse necceary to initiate self-focusing in the noble gas that fills the fiber. P_pump_scaled varies from 0-1. For why again read the published paper on this topic. 






Installation: 
Due to Luna.jl being written in Julia, and the BO algorithm in Python we have to make it so that a python code can run a Julia code and extract the produced data for analysis.



Dependencies: Open source library for Bayesian Optimisation in python: (https://github.com/bayesian-optimization/BayesianOptimization)

 Luna.jl (written in Julia) for simulating nonlinear dynamics in gas filled hollow capillary fibres. It uses pyJulia to let the two communicate (https://github.com/JuliaPy/pyjulia).
