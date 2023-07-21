# encoding: iso-8859-1
import os
import sys

def runEBkSP(num, scenario, outputDir):
    count = 0
    reroute = []
    reroute.append("EBkSP")
    while(count < len(reroute)):
        i = 0
        while(i < 1):
            output =("Outputs_%s/%s/reroute_%s_%d.xml"%(reroute[count], outputDir, reroute[count], i))
            os.system("python %s.py -c sumo -s %s/sim.sumocfg -n %s/sim.net.xml -k 3 -i 900 -b 1000 -e 10000 -d %d -o %s -l logs/%s.log"%(reroute[count], scenario, scenario, i, output, reroute[count]))
            i = i+1
        print("End simulation of %s"%(reroute[count]))
        count = count + 1
    print("End of all %d simulations"%(i))

def runGreenshield(num, scenario, outputDir, root):
    print("Greenshield\n")
    new_path = ("%s/Linear_models/Greenshield/"%(root))
    os.chdir(new_path)
    runEBkSP(num, scenario, outputDir)

def runDrake(num, scenario, outputDir, root):
    print("Drake\n")
    new_path = ("%s/Logarithm_models/Drake/"%(root))
    os.chdir(new_path)
    runEBkSP(num, scenario, outputDir)

def runGreenberg(num, scenario, outputDir, root):
    print("Greenberg\n")
    new_path = ("%s/Logarithm_models/Greenberg/"%(root))
    os.chdir(new_path)
    runEBkSP(num, scenario, outputDir)

def runGU(num, scenario, outputDir, root):
    print("Greenberg - Underwood\n")
    new_path = ("%s/Logarithm_models/Greenberg-Underwood/"%(root))
    os.chdir(new_path)
    runEBkSP(num, scenario, outputDir)

if __name__ == '__main__':
    root = os.getcwd()
    Chicago = ("%s/Chicago"%(root))
    Cologne = ("%s/Cologne"%(root))
    num = int(sys.argv[1])
    selected = []
    models = ["Greenshield", "Greenberg", "G/U", "Drake"]
    for argi in range(2, len(sys.argv)):
        i = sys.argv[argi]
        i = int(i)
        print(i)
        selected.append(models[i])
        
    scenario = Cologne
    outputDir = "Cologne"
    
    for model in selected:
        if(model == "Greenshield"):
            runGreenshield(num, scenario, outputDir, root)
        elif(model == "Greenberg"):
            runGreenberg(num, scenario, outputDir, root)
        elif(model == "G/U"):
            runGU(num, scenario, outputDir, root)
        elif(model == "Drake"):
            runDrake(num, scenario, outputDir, root)        
        

    print("Ended all models simulation")
    sys.exit()
