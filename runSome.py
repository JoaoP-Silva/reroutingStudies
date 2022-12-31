# encoding: iso-8859-1
import os
import sys

def runEBkSP(num, scenario, outputDir):
    count = 0
    reroute = []
    reroute.append("EBkSP")
    while(count < len(reroute)):
        i = 0
        while(i < num):
            output =("Outputs_%s/%s/reroute_%s_%d.xml"%(reroute[count], outputDir, reroute[count], i))
            os.system("python2 %s.py -c sumo -s %s/sim.sumocfg -n %s/sim.net.xml -k 3 -i 900 -b 1000 -e 10000 -d %d -o %s -l logs/%s.log"%(reroute[count], scenario, scenario, i, output, reroute[count]))
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

    print("Select the scenario to simulate:\n1.Chicago\t2.Cologne")
    sce_btn = int(input())
    scenario = Cologne
    outputDir = "Cologne"
    if(sce_btn == 1):
        scenario = Chicago
        outputDir = "Chicago"
    elif(sce_btn == 2):
        scenario = Cologne
        outputDir = "Cologne"
    
    models = []
    btn = -2
    display = ["1.Greenshield", "2.Greenberg", "3.G/U", "4.Drake"]
    while(btn != -1):
        print("Select models to run:\n")
        for item in display:
            print(("%s\t")%item)
        print("0. run")
        btn = int(input())
        btn = btn - 1
        if(btn >= 0):
            if(display[btn] == "1.Greenshield"):
                display[btn] = ""
                models.append("Greenshield")
            elif(display[btn] == "2.Greenberg"):
                display[btn] = ""
                models.append("Greenberg")
            elif(display[btn] == "3.G/U"):
                display[btn] = ""
                models.append("G/U")
            elif(display[btn] == "4.Drake"):
                display[btn] = ""
                models.append("Drake")

    for model in models:
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