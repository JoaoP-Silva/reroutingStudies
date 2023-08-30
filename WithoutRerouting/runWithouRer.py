import os
import sys
from paths import ROOT_PATH
sys.path.insert(1, ROOT_PATH)

def run(scenarioPath, scenario):
  
    os.system("python2 withoutRerouting.py -c sumo -s %s/sim.sumocfg -n %s/sim.net.xml -k 3 -i 900 -b 1000  -o %s_wout.xml -l norerouting.log"%( scenarioPath, scenarioPath, scenario))

if __name__ == '__main__':

    
    Chicago = ("%s/Chicago"%(ROOT_PATH))
    Cologne = ("%s/Cologne"%(ROOT_PATH))
    Monaco = ("%s/Monaco"%(ROOT_PATH))
    Luxembourg = ("%s/Luxembourg"%(ROOT_PATH))

    print("Select the scenario to simulate:\n1.Chicago\t2.Cologne\t3.Monaco\t4.Luxembourg")
    sce_btn = int(input())
    scenario = Luxembourg
    outputDir = "Luxembourg"

    if(sce_btn == 1):
        scenario = Chicago
        outputDir = "Chicago"

    elif(sce_btn == 2):
        scenario = Cologne
        outputDir = "Cologne"

    elif(sce_btn == 3):
        scenario = Monaco
        outputDir = "Monaco"
    
    elif(sce_btn == 4):
        scenario = Luxembourg
        outputDir = "Luxembourg"

    run(scenario, outputDir)