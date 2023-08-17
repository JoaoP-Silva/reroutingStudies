# encoding: iso-8859-1
import os
import sys

def runthis(num, scenario, outputDir):
    count = 0
    reroute = []
    reroute.append("DSP")
    reroute.append("RkSP")
    reroute.append("EBkSP")
    while(count < len(reroute)):
        i = 0
        while(i < num):
            output =("Outputs_%s/%s/reroute_%s_%d.xml"%(reroute[count], outputDir, reroute[count], i))
            if(reroute[count]) == "DSP":
                os.system("python2 %s.py -c sumo -s %s/sim.sumocfg -n %s/sim.net.xml -i 900 -b 1000 -e 10000 -d %d -o %s -l logs/%s.log"%(reroute[count], scenario, scenario, i, output, reroute[count]))
                i = i+1   
            else: 
                os.system("python2 %s.py -c sumo -s %s/sim.sumocfg -n %s/sim.net.xml -k 3 -i 900 -b 1000 -e 10000 -d %d -o %s -l logs/%s.log --scale 0.3"%(reroute[count], scenario, scenario, i, output, reroute[count]))
                i = i+1
        print("End simulation of %s"%(reroute[count]))
        count = count + 1
    print("End of all %d simulations"%(i))

if __name__ == '__main__':
    root = os.getcwd()

    Chicago = ("%s/Chicago"%(root))
    Cologne = ("%s/Cologne"%(root))
    Monaco = ("%s/Monaco"%(root))

    num = int(sys.argv[1])

    print("Select the scenario to simulate:\n1.Chicago\t2.Cologne\t3.Monaco")
    sce_btn = int(input())
    scenario = Cologne
    outputDir = "Cologne"

    if(sce_btn == 1):
        scenario = Chicago
        outputDir = "Chicago"

    elif(sce_btn == 2):
        scenario = Cologne
        outputDir = "Cologne"

    elif(sce_btn == 3):
        scenario = Monaco
        outputDir = "Monaco"

    print("Simulating the linear models\n")
    print("Greenshield\n")
    new_path = ("%s/Linear_models/Greenshield/"%(root))
    os.chdir(new_path)
    runthis(num, scenario, outputDir)
    print("Simulating the logarithm models\n")
    print("Drake\n")
    new_path = ("%s/Logarithm_models/Drake/"%(root))
    os.chdir(new_path)
    runthis(num, scenario, outputDir)
    print("Greenberg\n")
    new_path = ("%s/Logarithm_models/Greenberg/"%(root))
    os.chdir(new_path)
    runthis(num, scenario, outputDir)
    #print("Underwood\n")
    #new_path = ("%s/Logarithm_models/Underwood/"%(root))
    #os.chdir(new_path)
    #runthis(num, scenario)
    print("Greenberg - Underwood\n")
    new_path = ("%s/Logarithm_models/Greenberg-Underwood/"%(root))
    os.chdir(new_path)
    runthis(num, scenario, outputDir)
    print("Ended all models simulation")
    sys.exit()