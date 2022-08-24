# encoding: iso-8859-1
import os
import sys

def runthis(num, Chicago):
    count = 0
    reroute = []
    reroute.append("DSP")
    reroute.append("RkSP")
    reroute.append("EBkSP")
    while(count < len(reroute)):
        i = 0
        while(i < num):
            output =("Outputs_%s/reroute_%s_%d.xml"%(reroute[count], reroute[count], i))
            if(reroute[count]) == "DSP":
                os.system("python %s.py -s %s/sim.sumocfg -n %s/sim.net.xml -i 900 -b 1000 -e 10000 -d %d -o %s -l logs/%s.log"%(reroute[count], Chicago, Chicago, i, output, reroute[count]))
                i = i+1   
            else: 
                os.system("python %s.py -s %s/sim.sumocfg -n %s/sim.net.xml -k 3 -i 900 -b 1000 -e 10000 -d %d -o %s -l logs/%s.log"%(reroute[count], Chicago, Chicago, i, output, reroute[count]))
                i = i+1
        print("End simulation of %s"%(reroute[count]))
        count = count + 1
    print("End of all %d simulations"%(i))


if __name__ == '__main__':
    root = os.getcwd()
    Chicago = ("%s/Chicago"%(root))
    num = int(sys.argv[1])
    print("Simulating the linear models\n")
    print("Greenshield\n")
    new_path = ("%s/Linear_models/Greenshield/"%(root))
    os.chdir(new_path)
    runthis(num, Chicago)
    print("Other\n")
    new_path = ("%s/Linear_models/Other/"%(root))
    os.chdir(new_path)
    runthis(num, Chicago)
    print("Simulating the logarithm models\n")
    print("Drake\n")
    new_path = ("%s/Logarithm_models/Drake/"%(root))
    os.chdir(new_path)
    runthis(num, Chicago)
    print("Greenberg\n")
    new_path = ("%s/Logarithm_models/Greenberg/"%(root))
    os.chdir(new_path)
    runthis(num, Chicago)
    #print("Underwood\n")
    #new_path = ("%s/Logarithm_models/Underwood/"%(root))
    #os.chdir(new_path)
    #runthis(num, Chicago)
    print("Greenberg - Underwood\n")
    new_path = ("%s/Logarithm_models/Greenberg-Underwood/"%(root))
    os.chdir(new_path)
    runthis(num, Chicago)
    print("Ended all models simulation")
    sys.exit()