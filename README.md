# reroutingStudies
My implementations of centralized rerouting strategies using Python and SUMO.

## Rerouting strategies
The article "Proactive Vehicle Re-routing Strategies for Congestion Avoidance"(2012) describes three different aproachs related to vehicle rerouting: DSP, RkSP and EBkSP. Those strategies were implemented varying the math model used to predict road weight. Below, all codes directories are listed:
* [Initial solutions(not updated)](https://github.com/JoaoP-Silva/reroutingStudies/tree/main/Initial_solutions)
* [Linear models](https://github.com/JoaoP-Silva/reroutingStudies/tree/main/Linear_models)
* [Logarithm models](https://github.com/JoaoP-Silva/reroutingStudies/tree/main/Logarithm_models)

The script [runAll.py](https://github.com/JoaoP-Silva/reroutingStudies/blob/main/runAll.py) it's used to run all models with previously setted parameters. To use the script it's necessary pass an integer number $n$ as a paramater indicating the number of simulations (the SUMO random seed ranges from $0$ to $n$). Below is an example of the function's call to run 5 simulations:

```
runAll.py 5
```
## Other Scripts
* [genCharts.py](https://github.com/JoaoP-Silva/reroutingStudies/blob/main/genGraphics.py)(__python3 script__): Do bootstrap on data and generates differents images about the outputs. _Obs.:_ Uses pandas append (deprecated), in the future (i hope) it will be modified to pandas concat.

* [runSome.py](https://github.com/JoaoP-Silva/reroutingStudies/blob/main/runSome.py): Select the especific models to run in one simulation using EBkSP. Has the same function call as runAll.py.

## Packages and scenarios
- Sumo 0.30 is available in this [link](https://sourceforge.net/projects/sumo/files/sumo/version%200.30.0/). To install sumo run ```./configure``` then ``` make install ``` in sumo dir. Problems related with the HUGE constant in some src files can be solved changing it to DLB_MAX (check compiler extension for maximum double variable value). Sumo also requires [xerces](https://xerces.apache.org/xerces-c/) and [foxtoolkit](http://www.fox-toolkit.org/).

- Cologne scenario in NewCologne.zip file can be directly accessed [here](https://sourceforge.net/projects/sumo/files/traffic_data/scenarios/TAPASCologne/TAPASCologne-0.32.0.7z/download).
