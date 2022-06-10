#!/usr/bin/env python

from __future__ import division

import os
import sys
from paths import ROOT_PATH
sys.path.insert(1, ROOT_PATH)
import subprocess
import signal
import socket
import logging

from networkx.algorithms.traversal.breadth_first_search import bfs_edges
from numpy.lib.function_base import append
import thread
import time
import tempfile
import math
import random
import networkx as nx
import numpy as np
import random
import math
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

"""def terminate_sumo(sumo):
    if sumo.returncode == None:
        os.kill(sumo.pid, signal.SIGTERM)
        time.sleep(0.5)
        if sumo.returncode == None:
            os.kill(sumo.pid, signal.SIGKILL)
            time.sleep(1)
            if sumo.returncode == None:
                time.sleep(10)"""
    
    
    
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
            k_o = k_jam/2
            v_f = graph.edge[road][successor_road]["speed"]
            v = v_f * (1 - k_i/k_jam)
            t = road_length / v
            #teste peso negativo
            if(t <= 0):
                logging.debug("Peso negativo encontrado na aresta %s"%(road))
                logging.debug("k_i = %d\nk_j= %d\nv_f = %d"%(k_i, k_jam, v_f))
            graph.edge[road][successor_road]["weight"] = t
            network_capacity += k_jam
            edges_number += 1
            if(k_i/k_jam > k_o):
                graph.edge[road][successor_road]["congested"] = 1
                if(road.encode("ascii") not in congested_roads):
                    congested_roads.append(road.encode("ascii"))
            avg_cap = network_capacity/edges_number
        
                
                
                    

    return graph,congested_roads, avg_cap



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
    ODpairs = set()
    for road in congested_roads:
        cont = 0
        bfs = []
        roads_reroute = bfs_edges(graph, road, True)
        for lane in roads_reroute:
            if lane[1].startswith(":"): continue
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
                        source = traci.vehicle.getRoadID(vehicle)
                        route = traci.vehicle.getRoute(vehicle)
                        ODpair = (source, route[-1])
                        ODpairs.add(ODpair)

                          
    return vehicles_reroute, ODpairs

                
    

def calculate_RCI(graph, vehicle_route):
    travel_time = 0
    ff_travel_time = 0
    for i, road in enumerate(vehicle_route):
        if i != len(vehicle_route) - 1:
            travel_time += graph.edge[vehicle_route[i]][vehicle_route[i+1]]["weight"]
            if (graph.edge[vehicle_route[i]][vehicle_route[i+1]]["congested"] == 0):
                ff_travel_time += graph.edge[vehicle_route[i]][vehicle_route[i+1]]["weight"]

    RCI = (travel_time-ff_travel_time)/ff_travel_time
    return RCI



def calculate_ACI(graph, vehicle_route):
    travel_time = 0
    ff_travel_time = 0
    for i in range(len(vehicle_route)):
        if i != len(vehicle_route) - 1:
            travel_time += graph.edge[vehicle_route[i]][vehicle_route[i+1]]["weight"]
            if (graph.edge[vehicle_route[i]][vehicle_route[i+1]]["congested"] == 0):
                ff_travel_time += graph.edge[vehicle_route[i]][vehicle_route[i+1]]["weight"]

    ACI = travel_time-ff_travel_time
    return ACI     




def define_urgency(urgency,reroute_list, graph):
    list_cars = []
    if(urgency == 0):
        return 0
    for vehicle in reroute_list:
        route = traci.vehicle.getRoute(vehicle)
        if(urgency == 2):
            urgency_calc = calculate_ACI(graph, route)
            aux = (vehicle, urgency_calc)
            list_cars.append(aux)
        
        else:
            urgency_calc = calculate_RCI(graph, route)
            aux = (vehicle, urgency_calc)
            list_cars.append(aux)

    list_cars = sorted(list_cars, key=lambda car:car[1], reverse=True)
    ordenated_list = []
    for car in list_cars:
        ordenated_list.append(car[0])
    return ordenated_list



def getLeastPopularPath(kPaths, roadList, fcList, Cavg, graph):
    Popularity_list = []
    n = 0
    for fc in fcList:
        n += fc
    for path in kPaths:
        PathEv = 0
        for road in path:
            i = roadList.index(road)
            C_road = 0
            for successor_road in graph.successors_iter(road):
                road_length = graph.edge[road][successor_road]["length"]
                avr_car_length = traci.edge.getLastStepLength(road.encode("ascii"))
                # Assuming that min gap = 2.5m
                C_road = road_length/(avr_car_length + 2.5)
                break
            if fcList[i] == 0 or C_road ==0 : continue
            x = fcList[i]/n
            wi = Cavg/C_road
            PathEv += wi * x * math.log(x)
        PathEv = PathEv * -1
        try:
            PopPath = math.exp(PathEv)
        except:
            PopPath = float('inf')
        Popularity_list.append(PopPath)
    Least_popular_index = Popularity_list.index(min(Popularity_list))
    return kPaths[Least_popular_index]
    
        

def updateFootprint(Path, fcList, roadList):
    for road in Path:
        i = roadList.index(road)
        fcList[i] += 1
    return fcList
  
         
def calculate_all_paths(ODpairs, k, graph, all_paths):
    for pair in ODpairs:
        source = pair[0]
        destination = pair[1]
        k_paths = k_shortest_paths(graph, source, destination, k)
        for path in k_paths[1]:
            if path in all_paths: continue
            all_paths.append(path)
    return all_paths



def reroute_vehicles(allPaths, vehicle_list, avg_cap, graph, k):
    fc_list = []
    road_list = []
    initial = 1
    for path in allPaths:
        for road in path:
            if road not in road_list:
                road_list.append(road)
                fc_list.append(0)
        
    for vehicle in vehicle_list:
        k_paths = []
        route = traci.vehicle.getRoute(vehicle)
        source = traci.vehicle.getRoadID(vehicle)
        destination = route[-1]
        ODpair = (source, destination)
        for path in allPaths:
            p_source = path[0]
            p_dest = path[-1]
            p_ODpair = (p_source, p_dest)
            if p_ODpair == ODpair:
                k_paths.append(path)
                if(len(k_paths) == k):
                    break
        if initial == 1:
            traci.vehicle.setRoute(vehicle, k_paths[0])
            fc_list = updateFootprint(k_paths[0], fc_list, road_list)
            initial = 0
        else:
            new_route = getLeastPopularPath(k_paths, road_list, fc_list, avg_cap, graph)
            traci.vehicle.setRoute(vehicle, new_route)
            fc_list = updateFootprint(new_route, fc_list, road_list)

            
              
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
        
        if (int(step) == 100) or (int(step) == 150) or (int(step) == 200):
            save_image_file(output,step)
        
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
                all_paths = []
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
    
