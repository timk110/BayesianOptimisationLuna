

In Development: Note that this code is still a work in progress. I am cleaning it up to make it more readable by people other than myself.


Description: Resonant dispersive wave generation is a technique which has been recently applied to hollow capillary fibres. It allows for the generation of ultrashort laser pulses of < 5 fs with central wavelengths < 300 nm. It involves sending a pump pulse at a longer wavelength into a hollow capillary fibre filled with a noble gas. The nonlinear dynamics that occur when the pump pulse interacts with the medium can lead to the generation of a near transform limited laser pulse at a much shorter wavelength. However, due to the inherently nonlinear nature of the dynamics that occur in this system, it is very difficult to predict analytically what system parameters are required to generate the optimal RDW (optimal here we define as highest peak power, close to gaussian temporal pulse shape and a pulse duration of < 5fs).The


This is where optimisation algorithms come into play. These algorithms are designed to identify the values of a functions variables that maximise said function. Here we are using Bayesian optimisation (BO). Luna.jl is a open source code base written in Julia that allows for the simulation of nonlinear processes in hollow capillary fibres, which includes RDW generation. Therefore by combining BO with Luna.jl we can let the optimisation algorithm determine what the 
Installation: 

Quickstart : TBA 
Complications: 


Dependencies: This code uses the open source library for Bayesian Optimisation in python (https://github.com/bayesian-optimization/BayesianOptimization)
and Luna.jl (written in Julia) for simulating nonlinear dynamics in gas filled hollow capillary fibres. It uses pyJulia to let the two communicate (https://github.com/JuliaPy/pyjulia).
