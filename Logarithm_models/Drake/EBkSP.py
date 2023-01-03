#!/usr/bin/env python

from __future__ import division

import os
import sys
from paths import ROOT_PATH
sys.path.insert(1, ROOT_PATH)
from EBkSP_functions import *
import subprocess
import socket
import logging

import thread
import time

from optparse import OptionParser




def update_travel_time_on_roads(graph, time, begin_of_cycle):
    congested_roads = set()
    network_capacity = 0
    edges_number = 0
    for road in graph.nodes_iter():
        if road.startswith(":"): continue
        for successor_road in graph.successors_iter(road):
            # If it is the first measurement in a cycle, then do not compute the mean
            road_length = graph.edge[road][successor_road]["length"]
            k_i = traci.edge.getLastStepVehicleNumber(road.encode("ascii"))
            avr_car_length = traci.edge.getLastStepLength(road.encode("ascii"))
            # Assuming that min gap = 2.5m
            k_jam = road_length/(avr_car_length + 2.5)
            if k_i >= k_jam:
                k_i = k_jam - 0.1
            k_o = k_jam/math.e
            v_f = graph.edge[road][successor_road]["speed"]
            v = v_f * math.exp((-1/2) * ((k_i/k_o)**2))
            t = road_length / v
            graph.edge[road][successor_road]["weight"] = t
            network_capacity += k_jam
            edges_number += 1
            if(k_i/k_jam > k_o):
                graph.edge[road][successor_road]["congested"] = 1
                if(road.encode("ascii") not in congested_roads):
                    congested_roads.add(road.encode("ascii"))
            avg_cap = network_capacity/edges_number
        
    return graph,congested_roads, avg_cap



os.environ["SUMO_HOME"] = "/home/joao/Sumo/sumo-0.30.0"

# We need to import Python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Environment variable SUMO_HOME not defined")
    
import traci

class UnusedPortLock:
    lock = thread.allocate_lock()

    def __init__(self):
        self.acquired = False

    def __enter__(self):
        self.acquire()

    def __exit__(self):
        self.release()

    def acquire(self):
        if not self.acquired:
            UnusedPortLock.lock.acquire()
            self.acquired = True

    def release(self):
        if self.acquired:
            UnusedPortLock.lock.release()
            self.acquired = False


def find_unused_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.bind(('127.0.0.1', 0))
    sock.listen(socket.SOMAXCONN)
    ipaddr, port = sock.getsockname()
    sock.close()
    
    return port

"""def terminate_sumo(sumo):
    if sumo.returncode == None:
        os.kill(sumo.pid, signal.SIGTERM)
        time.sleep(0.5)
        if sumo.returncode == None:
            os.kill(sumo.pid, signal.SIGKILL)
            time.sleep(1)
            if sumo.returncode == None:
                time.sleep(10)"""
    
                         
def run(network, begin, end, interval, t, output, probability, vnumber, k_paths, level, urgency):
    logging.debug("Building road graph")         
    road_graph_travel_time = build_road_graph(network)
    logging.debug("Finding all simple paths")
    
    # Used to enhance performance only
    buffered_paths = {}
    
    logging.debug("Running simulation now")    
    # The time at which the first re-routing will happen
    # The time at which a cycle for collecting travel time measurements begins
    travel_time_cycle_begin = interval


    #flag = 0
    step = 1
    while (step == 1 or traci.simulation.getMinExpectedNumber() > 0):

        logging.debug("Minimum expected number of vehicles: %d" % traci.simulation.getMinExpectedNumber())
        traci.simulationStep()

        #if step % LOG_CARROS_RUAS == 0:
        #    log_qnt_carros_ruas(step)
        

        # Se time > 0, simular X carros por time segundos.
        #if t > 0 and step > t + 1:
        #    flag = 1
        
        #log_densidade_speed(step) 
        logging.debug("Simulation time %d" % step)
        if step >= travel_time_cycle_begin and travel_time_cycle_begin <= end and step%interval == 0:
            logging.debug("Updating travel time on roads at simulation time %d" % step)
            updated_graph = update_travel_time_on_roads(road_graph_travel_time, step, travel_time_cycle_begin == step)
            road_graph_travel_time = updated_graph[0]
            congested_roads = updated_graph[1]
            avg_capacity = updated_graph[2]
            if(len(congested_roads)>0):
                candidates_and_ODpairs = gen_canditates_reroute(road_graph_travel_time,congested_roads, level)
                candidates_reroute = candidates_and_ODpairs[0]
                candidates_reroute = define_urgency(urgency, candidates_reroute, road_graph_travel_time)
                ODpairs = candidates_and_ODpairs[1]
                all_paths = {}
                all_paths = calculate_all_paths(ODpairs, k_paths, road_graph_travel_time, all_paths)
            
                #if step >= travel_time_cycle_begin and travel_time_cycle_begin <= end and step%interval == 0:
                logging.debug("Updating travel time on roads at simulation time %d" % step)
                print ("\nEBkSP " , step, "  REROUTE")
                reroute_vehicles(all_paths, candidates_reroute, avg_capacity, road_graph_travel_time, k_paths)          


        #if step%100 == 0:
        #    save_image_file(output, step)


        step += 1     
                             
    #save_log_qnt_carros_ruas(output,step)
          
    sys.stdout.flush()
    time.sleep(10)
    logging.debug("Simulation finished")
    traci.close()
    sys.stdout.flush()
    time.sleep(10)
        
def start_simulation(sumo, scenario, network, begin, end, interval, output, vnumber, time, probability, k_paths, level, urgency, seed):
    logging.debug("Finding unused port")
    
    unused_port_lock = UnusedPortLock()
    unused_port_lock.__enter__()
    remote_port = find_unused_port()
    
    logging.debug("Port %d was found" % remote_port)
    
    logging.debug("Starting SUMO as a server")
    
       
    #sumo = subprocess.Popen([sumo, "-c", scenario, "--tripinfo-output", output, "--device.emissions.probability", "1.0", "--remote-port", str(remote_port)], stdout=sys.stdout, stderr=sys.stderr)    
    
    
    
    if time == 0:
        create_vehicle_dict_probability(probability, vnumber)
        sumo = subprocess.Popen([sumo, "-c", scenario, "--tripinfo-output", output,"--seed", str(seed), "--device.emissions.probability", "1.0", "--remote-port", str(remote_port)], stdout=sys.stdout, stderr=sys.stderr)    
    else:
        create_vehicle_dict_probability(probability, 35000)
        sumo = subprocess.Popen([sumo, "-c", scenario, "--max-num-vehicles", str(vnumber),"--tripinfo-output", output, "--vehroute-output", output, "--seed", str(seed), "--device.emissions.probability", "1.0","--full-output","output.xml", "--remote-port", str(remote_port)], stdout=sys.stdout, stderr=sys.stderr)
        
    
    
    
    unused_port_lock.release()
            
    try:     
        traci.init(remote_port)    
        run(network, begin, end, interval, time, output, probability, vnumber, k_paths, level, urgency)
    except Exception as e:
        logging.exception("Something bad happened")
    finally:
        logging.exception("Terminating SUMO")  
        print("Simulation finished")
        unused_port_lock.__exit__()
        
def main():
        
    # Option handling
    parser = OptionParser()
    parser.add_option("-c", "--command", dest="command", default="sumo.exe", help="The command used to run SUMO [default: %d efault]", metavar="COMMAND")
    parser.add_option("-s", "--scenario", dest="scenario", default="Chicago/sim.sumocfg", help="A SUMO configuration file [default: %default]", metavar="FILE")
    parser.add_option("-n", "--network", dest="network", default="Chicago/sim.net.xml", help="A SUMO network definition file [default: %default]", metavar="FILE")    
    parser.add_option("-b", "--begin", dest="begin", type="int", default=1000, action="store", help="The simulation time (s) at which the re-routing begins [default: %default]", metavar="BEGIN")
    parser.add_option("-e", "--end", dest="end", type="int", default=10000, action="store", help="The simulation time (s) at which the re-routing ends [default: %default]", metavar="END")
    parser.add_option("-i", "--interval", dest="interval", type="int", default=900, action="store", help="The interval (s) of classification [default: %default]", metavar="INTERVAL")
    parser.add_option("-o", "--output", dest="output", default="Outputs_EBkSP/reroute_ebksp", help="The XML file at which the output must be written [default: %default]", metavar="FILE")
    parser.add_option("-l", "--logfile", dest="logfile", default="EBkSP-log.txt", help="log messages to logfile [default: %default]", metavar="FILE")
    parser.add_option("-v", "--vehicle-number", dest="vnumber", type="int", default=0, action="store", help="Number of vehicles in the network [default: %default]", metavar="FILE")
    parser.add_option("-t", "--time", dest="time", type="int", default=0, action="store", help="Time to maintain the number of vehicles in the network [default: %default]", metavar="FILE")
    parser.add_option("-p", "--probability", dest="probability", type="float", default=1.0, action="store", help="Probability to accept a new route [default: %default]", metavar="FILE")
    parser.add_option("-r", "--blockead_road", dest="blockead_road", default="Chicago/sim.net.xml", help="A SUMO network definition file [default: %default]", metavar="FILE")
    parser.add_option("-k", "--k_paths", dest="k_paths",type="int", default= 3, help="A variable to set the number of paths generate to reroute [default: %default]", metavar="FILE")
    parser.add_option("--level", dest="level", type="int", default = 3 , action="store", help="A level to decide how far from congestion to look for candidates for re-routing [default: %default]", metavar="FILE")
    parser.add_option("--urgency", dest="urgency", type="int", default= 2, action="store", help="A variable to set the type of urgency considered. 0 = none, 1 = RCI, 2 = ACI  [default: %default]", metavar="FILE")
    parser.add_option("-d", "--seed", dest="seed", type="int", default=0, action="store", help="The seed used to initialize the basic random number generator [default: %default]", metavar="SEED")
    
    (options, args) = parser.parse_args()
    
    logging.basicConfig(filename=options.logfile, level=logging.DEBUG)
    logging.debug("Logging to %s" % options.logfile)
    
    if args:
        logging.warning("Superfluous command line arguments: \"%s\"" % " ".join(args))
        
    start_simulation(options.command, options.scenario, options.network, options.begin, options.end, options.interval, options.output, options.vnumber, options.time, options.probability, options.k_paths, options.level, options.urgency, options.seed)
    
if __name__ == "__main__":
    main()    
    