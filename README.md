# reroutingStudies
My implementations of centralized rerouting strategies using Python(v2.7) and SUMO(v0.30).

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
* [genGraphics.py](https://github.com/JoaoP-Silva/reroutingStudies/blob/main/genGraphics.py): Do bootstrap on data and generates differents graphs about the outputs.
* [runSome.py](https://github.com/JoaoP-Silva/reroutingStudies/blob/main/runSome.py): Select the especific models to run in one simulation.
