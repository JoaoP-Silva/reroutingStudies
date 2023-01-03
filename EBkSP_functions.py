#!/usr/bin/env python

from __future__ import division

import os
import sys

from networkx.algorithms.traversal.breadth_first_search import bfs_edges
import random
import networkx as nx
import math

from k_shortest_paths import k_shortest_paths
from bs4 import BeautifulSoup

os.environ["SUMO_HOME"] = "/home/joao/Sumo/sumo-0.30.0"

# We need to import Python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Environment variable SUMO_HOME not defined")
    
import traci


CAR_SIZE = 5
GAP = 2.5       


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


vehicles_p = {}
def create_vehicle_dict_probability(probability, vnumber):
    
    for i in range (0,vnumber):
        vehicles_p[str(i)] = random.random()



def gen_canditates_reroute(graph, congested_roads, level):
    reverseGraph = nx.DiGraph.reverse(graph)
    vehicles_reroute = set()
    ODpairs = set()
    for road in congested_roads:
        cont = 0
        bfs = []
        roads_reroute = bfs_edges(reverseGraph, road, True)
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
                        vehicles_reroute.add(vehicle)
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



def getLeastPopularPath(kPaths, fcDict, Cavg, graph):
    leastPopularValue = float('inf')
    leastPopularIdx = 0
    n = 0
    i = -1
    for road in fcDict:
        n += fcDict[road]
    for path in kPaths:
        PathEv = 0
        i += 1
        for road in path:
            C_road = 0
            for successor_road in graph.successors_iter(road):
                road_length = graph.edge[road][successor_road]["length"]
                avr_car_length = traci.edge.getLastStepLength(road.encode("ascii"))
                # Assuming that min gap = 2.5m
                C_road = road_length/(avr_car_length + 2.5)
                break
            if(road in fcDict and C_road > 0) :
                x = fcDict[road]/n
                wi = Cavg/C_road
                PathEv += wi * x * math.log(x)
        PathEv = PathEv * -1
        try:
            PopPath = math.exp(PathEv)
        except:
            PopPath = float('inf')

        if(PopPath < leastPopularValue):
            leastPopularValue = PopPath
            leastPopularIdx = i
    return kPaths[i]
    
        

def updateFootprint(Path, fcDict):
    for road in Path:
        if(road not in fcDict):
            fcDict[road] = 1
        else:
            fcDict[road] += 1
    return fcDict
  
         
def calculate_all_paths(ODpairs, k, graph, all_paths):
    for pair in ODpairs:
        source = pair[0]
        destination = pair[1]

        if source != destination:
            k_paths = k_shortest_paths(graph, source, destination, k)
            all_paths[(source, destination)] = k_paths[1]
            
    return all_paths



def reroute_vehicles(allPaths, vehicle_list, avg_cap, graph, k):

    fc_dict = {}
    initial = 1

    for vehicle in vehicle_list:
        k_paths = []
        route = traci.vehicle.getRoute(vehicle)
        source = traci.vehicle.getRoadID(vehicle)
        destination = route[-1]
        if(source == destination): continue
        ODpair = (source, destination)
        k_paths = allPaths[ODpair]

        if initial == 1:
            traci.vehicle.setRoute(vehicle, k_paths[0])
            fc_dict = updateFootprint(k_paths[0], fc_dict)
            initial = 0
        else:
            new_route = getLeastPopularPath(k_paths, fc_dict, avg_cap, graph)
            traci.vehicle.setRoute(vehicle, new_route)
            fc_dict = updateFootprint(new_route, fc_dict)