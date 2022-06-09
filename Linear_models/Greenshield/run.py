# encoding: iso-8859-1
import os
import sys
from paths import LOCAL_PATH
if __name__ == '__main__':
    num = int(sys.argv[1])
    count = 0
    reroute = []
    reroute.append("DSP")
    reroute.append("RkSP")
    reroute.append("EBkSP")
    path = u"c:\\Users\\joope\\OneDrive\\Área de Trabalho\\Projetos\\Iniciação Cienctífica - STI\\codes\\Linear_models\\Greenshield\\"
    while(count < len(reroute)):
        i = 0
        while(i < num):
            output =("Outputs_%s/reroute_%s_%d.xml"%(reroute[count], reroute[count], i))
            if(reroute[count]) == "DSP":
                os.system("python %s%s.py -s Chicago/sim.sumocfg -n Chicago/sim.net.xml -i 900 -b 1000 -e 10000 -d %d -o %s -l logs/%s.log"%(path.decode('cp1252'), reroute[count], i, output, reroute[count]))
                i = i+1   
            else: 
                os.system("python %s%s.py -s Chicago/sim.sumocfg -n Chicago/sim.net.xml -k 3 -i 900 -b 1000 -e 10000 -d %d -o %s -l logs/%s.log"%(path.decode('cp1252'), reroute[count], i, output, reroute[count]))
                i = i+1
        print("End simulation of %s"%(reroute[count]))
        count = count + 1
    print("End of all %d simulations"%(i))
    sys.exit()