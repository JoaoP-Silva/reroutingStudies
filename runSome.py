# encoding: iso-8859-1
import os
import sys

def runEBkSP(num, model, scenario, outputDir):
    count = 0
    reroute = []
    reroute.append("EBkSP")
    while(count < len(reroute)):
        i = 0
        while(i < num):
            output =("Outputs_%s/%s/reroute_%s_%d.xml"%(reroute[count], outputDir, reroute[count], i))
            os.system("python %s.py -c sumo -s %s/sim.sumocfg -n %s/sim.net.xml -k 3 -i 900 -b 1000 -d %d -o %s -l logs/%s_%s_%d.log --scale 0.75"%(reroute[count], scenario, scenario, i, output, reroute[count], model, num))
            i = i+1
        print("End simulation of %s"%(reroute[count]))
        count = count + 1
    print("End of all %d simulations"%(i))

if __name__ == '__main__':
    root = os.getcwd()

    Chicago = ("%s/Chicago"%(root))
    Cologne = ("%s/Cologne"%(root))
    Monaco = ("%s/Monaco"%(root))
    Luxembourg = ("%s/Luxembourg"%(root))

    num = int(sys.argv[1])
    selected = []
    models = ["Greenshield", "Greenberg", "G/U", "Drake"]
    for argi in range(2, len(sys.argv)):
        i = sys.argv[argi]
        i = int(i)
        print(i)
        selected.append(models[i])
        
    scenario = Luxembourg
    outputDir = "Luxembourg"
    
    for model in selected:
        if(model == "Greenshield"):
            print("Greenshield\n")
            new_path = ("%s/Linear_models/Greenshield/"%(root))
            os.chdir(new_path)
            runEBkSP(num, model, scenario, outputDir)

        elif(model == "Greenberg"):
            print("Greenberg\n")
            new_path = ("%s/Logarithm_models/Greenberg/"%(root))
            os.chdir(new_path)
            runEBkSP(num, model, scenario, outputDir)

        elif(model == "G/U"):
            print("Greenberg - Underwood\n")
            new_path = ("%s/Logarithm_models/Greenberg-Underwood/"%(root))
            os.chdir(new_path)
            runEBkSP(num, model, scenario, outputDir)

        elif(model == "Drake"):
            print("Drake\n")
            new_path = ("%s/Logarithm_models/Drake/"%(root))
            os.chdir(new_path)
            runEBkSP(num, model, scenario, outputDir)        
        

    print("Ended all models simulation")
    sys.exit()
