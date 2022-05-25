#!/usr/bin/env python

from __future__ import division

import os
import sys
import subprocess
import signal
import socket
import logging

from networkx.algorithms.traversal.breadth_first_search import bfs_edges
import thread
import time
import tempfile
import math
import random
import networkx as nx
import numpy as np

LOG_CARROS_RUAS = 100

from k_shortest_paths import k_shortest_paths
from optparse import OptionParser
from bs4 import BeautifulSoup

#os.environ["SUMO_HOME"]="/home/guidoni/sumo/Journal/sumo-0.25.0"
#os.environ["SUMO_HOME"]="/Users/guidoni/Documents/workspace/IEEE TVT/sumo-0.27.1"


SUMO_HOME ="/c:/Eclipse/sumo-.30"

# We need to import Python modules from the $SUMO_HOME/tools directory
""" if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Environment variable SUMO_HOME not defined") """
    
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

def terminate_sumo(sumo):
    if sumo.returncode == None:
        os.kill(sumo.pid, signal.SIGTERM)
        time.sleep(0.5)
        if sumo.returncode == None:
            os.kill(sumo.pid, signal.SIGKILL)
            time.sleep(1)
            if sumo.returncode == None:
                time.sleep(10)
    
    
    
edges_length = {}
edges_lane = {}
edges_speed = {}
def build_road_graph(network):                
    # Input   
    f = open(network)
    data = f.read()
    soup = BeautifulSoup(data, 'lxml')

    f.close()

    for edge_tag in soup.findAll("edge"):
        lane_tag = edge_tag.find("lane")
              
        edge_id = edge_tag["id"]
        edge_length = float(lane_tag["length"])
        
        edges_length[edge_id] = edge_length
        
        #teste daniel
        num_lane_tag = edge_tag.findAll("lane")
        edges_lane[edge_id] = len(num_lane_tag)

        edge_speed = float(lane_tag["speed"])
        edges_speed[edge_id] = edge_speed

    graph = nx.DiGraph()            

    for connection_tag in soup.findAll("connection"):
        source_edge = connection_tag["from"]        
        dest_edge = connection_tag["to"]
        #print source_edge, dest_edge, edges_length[source_edge]
        graph.add_edge(source_edge.encode("ascii"), dest_edge.encode("ascii"), length=edges_length[source_edge], weight=0, congested = 0, speed = edges_speed[source_edge])
        

    return graph          
 

def log_densidade_speed(time):
    vehicles = traci.vehicle.getIDList()
    density = len(vehicles)
    speed = []

    output = open('output/average_speed_DSP.txt', 'a')

    for v in vehicles:
        lane_pos = traci.vehicle.getLanePosition(v)
        edge = traci.vehicle.getRoadID(v)
        if edge.startswith(":"): continue
        position = traci.vehicle.getPosition(v)        
        route = traci.vehicle.getRoute(v)
        index = route.index(edge)
        if index > 0:
            distance = 500 * (index - 1) + lane_pos
        else:
            distance = lane_pos

        traveltime = traci.vehicle.getAdaptedTraveltime(v, time, edge)
        speed.append(float(distance)/float(time))
    
    output.write(str(np.amin(speed) * 3.6) + '\t' + str(np.average(speed) * 3.6) + '\t' + str(np.amax(speed) * 3.6) + '\t' + str(density)+'\n')

def update_travel_time_on_roads(graph, time, begin_of_cycle):
    congested_roads = []
    for road in graph.nodes_iter():
        travel_time = traci.edge.getAdaptedTraveltime(road.encode("ascii"), time)
        if travel_time <= 0:
            travel_time = traci.edge.getTraveltime(road.encode("ascii"))
        if road.startswith(":"): continue
        for successor_road in graph.successors_iter(road):
            # If it is the first measurement in a cycle, then do not compute the mean
            road_length = graph.edge[road][successor_road]["length"]
            k_i = traci.edge.getLastStepVehicleNumber(road.encode("ascii"))
            avr_car_length = traci.edge.getLastStepLength(road.encode("ascii"))
            # Assuming that min gap = 2.5m
            k_jam = road_length/(avr_car_length + 2.5)
            k_o = k_jam/2
            v_f = graph.edge[road][successor_road]["speed"]
            v = v_f * (1 - k_i/k_jam)
            t = road_length / v
            if begin_of_cycle:
                graph.edge[road][successor_road]["weight"] = travel_time
            else:
                graph.edge[road][successor_road]["weight"] = t
            if(k_i/k_jam > k_o):
                graph.edge[road][successor_road]["congested"] = 1
                if(road.encode("ascii") not in congested_roads):
                    congested_roads.append(road.encode("ascii"))
        
                
                
                    

    return graph,congested_roads



carros_ruas = {}
CAR_SIZE = 5
GAP = 2.5
def log_qnt_carros_ruas(step):
    
    carros_ruas[step] = {}
    for i in range(0,11):
        carros_ruas[step][i] = 0
    
    edges = traci.edge.getIDList()
    
    for e in edges:
        
        if e.startswith(":"):
            continue
        
        num_vehicles = traci.edge.getLastStepVehicleNumber(e)
        edge_length = edges_length[e]
        num_max_vehicles = math.floor(edge_length / float(CAR_SIZE+GAP))
        if num_max_vehicles != 0:
            usage = (num_vehicles * 100) / (num_max_vehicles*edges_lane[e])
        else:
            usage = 0

 
        if edge_length > 100: # descartar edges muito pequenas
            if usage == 0:
                carros_ruas[step][0] += 1
            elif 0 < usage <= 10:
                carros_ruas[step][1] += 1
            elif 10 < usage <= 20:
                carros_ruas[step][2] += 1
            elif 20 < usage <= 30:
                carros_ruas[step][3] += 1
            elif 30 < usage <= 40:
                carros_ruas[step][4] += 1
            elif 40 < usage <= 50:
                carros_ruas[step][5] += 1
            elif 50 < usage <= 60:
                carros_ruas[step][6] += 1
            elif 60 < usage <= 70:
                carros_ruas[step][7] += 1
            elif 70 < usage <= 80:
                carros_ruas[step][8] += 1
            elif 80 < usage <= 90:
                carros_ruas[step][9] += 1
            else:
                carros_ruas[step][10] += 1
        
        

def save_log_qnt_carros_ruas(output,step):
    filename = output.replace("xml", "qcr")
    f = open(filename, "w")
    line = ""
    for i in range(1,step):
        if i % LOG_CARROS_RUAS == 0:
            line += str(i)
            for k in range(0,11):
                line += "\t" + str(carros_ruas[i][k])
            line += "\n"
            
    f.write(line)
    f.close()             


def save_image_file(output,step):
    print ("save img file. step = ", step)
    filename = output.replace(".xml", "_" + str(step) + "_img.txt")
    f = open(filename, "w")
    line = ""
    line  += str(len(traci.vehicle.getIDList())) + "\n"
    lanes = traci.lane.getIDList()
    for lane in lanes:
        occupancy = traci.lane.getLastStepOccupancy(lane)
        line += lane + "\t" + str(occupancy) + "\n"
            
    f.write(line)
    f.close()



vehicles_p = {}
def create_vehicle_dict_probability(probability, vnumber):
    
    for i in range (0,vnumber):
        vehicles_p[str(i)] = random.random()



def gen_canditates_reroute(graph, congested_roads, level):
    vehicles_reroute = []
    for road in congested_roads:
        cont = 0
        bfs = []
        roads_reroute = bfs_edges(graph, road, True)
        for lane in roads_reroute:
            if(lane[0] in bfs):
                cont = cont + 1
                bfs = []
            if(cont==level):
                break
            bfs.append(lane[1])
            vehicles_in_the_lane = traci.edge.getLastStepVehicleIDs(lane[1].encode("ascii"))
            #If is the first iteration in the loop, 
            if(cont == 0 and lane[0] not in bfs):
                vehicles_in_the_lane += traci.edge.getLastStepVehicleIDs(lane[0].encode("ascii"))
            if(len(vehicles_in_the_lane)>0):
                for vehicle in vehicles_in_the_lane:
                    if(vehicle not in vehicles_reroute):
                        vehicles_reroute.append(vehicle)
    
    
    return vehicles_reroute





def reroute_vehicles(list_vehicles, graph, probability):
    ####simple_paths = []

    for vehicle in list_vehicles:
        
        #if vehicles_p[vehicle] > probability:
        #    continue
        
        source = traci.vehicle.getRoadID(vehicle)
        if source.startswith(":"): continue
        route = traci.vehicle.getRoute(vehicle)
        destination = route[-1]
                                        
        if source != destination:
            logging.debug("Calculating shortest paths for pair (%s, %s)" % (source, destination))
            new_route = nx.dijkstra_path(graph, source, destination)
            traci.vehicle.setRoute(vehicle, new_route)   
  
         
    

              
def run(network, begin, end, interval, t, output, probability, vnumber, level):
    logging.debug("Building road graph")         
    road_graph_travel_time = build_road_graph(network)
    logging.debug("Finding all simple paths")
    
    # Used to enhance performance only
    buffered_paths = {}
    
    logging.debug("Running simulation now")    
    # The time at which the first re-routing will happen
    # The time at which a cycle for collecting travel time measurements begins
    travel_time_cycle_begin = interval




    flag = 0
    step = 1
    while (step == 1 or traci.simulation.getMinExpectedNumber() > 0) and flag == 0:

        logging.debug("Minimum expected number of vehicles: %d" % traci.simulation.getMinExpectedNumber())
        traci.simulationStep()

        #if step % LOG_CARROS_RUAS == 0:
        #    log_qnt_carros_ruas(step)
        

        # Se time > 0, simular X carros por time segundos.
        if t > 0 and step > t + 1:
            flag = 1
        
        if (int(step) == 100) or (int(step) == 150) or (int(step) == 200):
            save_image_file(output,step)
        
        #log_densidade_speed(step) 
        logging.debug("Simulation time %d" % step)
        if step >= travel_time_cycle_begin and travel_time_cycle_begin <= end and step%interval == 0:
            logging.debug("Updating travel time on roads at simulation time %d" % step)
            updated_graph = update_travel_time_on_roads(road_graph_travel_time, step, travel_time_cycle_begin == step)
            road_graph_travel_time = updated_graph[0]
            congested_roads = updated_graph[1]
            candidates_reroute = gen_canditates_reroute(road_graph_travel_time,congested_roads, level)
            #candidates_reroute = define_urgency(urgency, congested_roads, candidates_reroute, road_graph_travel_time)

            #if step >= travel_time_cycle_begin and travel_time_cycle_begin <= end and step%interval == 0:
            logging.debug("Updating travel time on roads at simulation time %d" % step)
            print ("\nDSP " , step, "  REROUTE")
            reroute_vehicles(candidates_reroute, road_graph_travel_time, probability)           


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
        
def start_simulation(sumo, scenario, network, begin, end, interval, output, vnumber, time, probability, seed, level):
    logging.debug("Finding unused port")
    
    unused_port_lock = UnusedPortLock()
    unused_port_lock.__enter__()
    remote_port = find_unused_port()
    
    logging.debug("Port %d was found" % remote_port)
    
    logging.debug("Starting SUMO as a server")
    
       
    #sumo = subprocess.Popen([sumo, "-c", scenario, "--tripinfo-output", output, "--device.emissions.probability", "1.0", "--remote-port", str(remote_port)], stdout=sys.stdout, stderr=sys.stderr)    
    
    
    
    if time == 0:
        create_vehicle_dict_probability(probability, vnumber)
        sumo = subprocess.Popen([sumo, "-c", scenario, "--tripinfo-output", output, "--vehroute-output", output,"--seed", seed, "--device.emissions.probability", "1.0", "--remote-port", str(remote_port)], stdout=sys.stdout, stderr=sys.stderr)    
    else:
        create_vehicle_dict_probability(probability, 35000)
        sumo = subprocess.Popen([sumo, "-c", scenario, "--max-num-vehicles", str(vnumber),"--tripinfo-output", output, "--vehroute-output", output,"--seed", seed, "--device.emissions.probability", "1.0", "--remote-port", str(remote_port)], stdout=sys.stdout, stderr=sys.stderr)
        
    
    
    
    unused_port_lock.release()
            
    try:     
        traci.init(remote_port)    
        run(network, begin, end, interval, time, output, probability, vnumber, level)
    except Exception as e:
        logging.exception("Something bad happened")
    finally:
        logging.exception("Terminating SUMO")  
        terminate_sumo(sumo)
        unused_port_lock.__exit__()
        
def main():
        
    # Option handling
    parser = OptionParser()
    parser.add_option("-c", "--command", dest="command", default="sumo.exe", help="The command used to run SUMO [default: %d efault]", metavar="COMMAND")
    parser.add_option("-s", "--scenario", dest="scenario", default="500_0.sumo.cfg", help="A SUMO configuration file [default: %default]", metavar="FILE")
    parser.add_option("-n", "--network", dest="network", default="network.net.xml", help="A SUMO network definition file [default: %default]", metavar="FILE")    
    parser.add_option("-b", "--begin", dest="begin", type="int", default=0, action="store", help="The simulation time (s) at which the re-routing begins [default: %default]", metavar="BEGIN")
    parser.add_option("-e", "--end", dest="end", type="int", default=280, action="store", help="The simulation time (s) at which the re-routing ends [default: %default]", metavar="END")
    parser.add_option("-i", "--interval", dest="interval", type="int", default=10, action="store", help="The interval (s) of classification [default: %default]", metavar="INTERVAL")
    parser.add_option("-o", "--output", dest="output", default="reroute.xml", help="The XML file at which the output must be written [default: %default]", metavar="FILE")
    parser.add_option("-l", "--logfile", dest="logfile", default="logs/DSP.log", help="log messages to logfile [default: %default]", metavar="FILE")
    parser.add_option("-v", "--vehicle-number", dest="vnumber", type="int", default=0, action="store", help="Number of vehicles in the network [default: %default]", metavar="FILE")
    parser.add_option("-t", "--time", dest="time", type="int", default=0, action="store", help="Time to maintain the number of vehicles in the network [default: %default]", metavar="FILE")
    parser.add_option("-p", "--probability", dest="probability", type="float", default=1.0, action="store", help="Probability to accept a new route [default: %default]", metavar="FILE")
    parser.add_option("-r", "--blockead_road", dest="blockead_road", default="network.net.xml", help="A SUMO network definition file [default: %default]", metavar="FILE")
    parser.add_option("-d", "--seed", dest="seed", type="int", default=0, action="store", help="The seed used to initialize the basic random number generator [default: %default]", metavar="SEED")
    parser.add_option("--level", dest="level", type="int", default=3, action="store", help="A level to decide how far from congestion to look for candidates for re-routing [default: %default]", metavar="FILE")
    (options, args) = parser.parse_args()
    
    logging.basicConfig(filename=options.logfile, level=logging.DEBUG)
    logging.debug("Logging to %s" % options.logfile)
    
    if args:
        logging.warning("Superfluous command line arguments: \"%s\"" % " ".join(args))
        
    start_simulation(options.command, options.scenario, options.network, options.begin, options.end, options.interval, options.output, options.vnumber, options.time, options.probability, options.level, options.seed)
    
if __name__ == "__main__":
    main()    
    
