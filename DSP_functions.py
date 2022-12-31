#!/usr/bin/env python

from __future__ import division

import os
import sys

from networkx.algorithms.traversal.breadth_first_search import bfs_edges
from numpy.lib.function_base import append
import random
import networkx as nx
import logging

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
        graph.add_edge(source_edge.encode("ascii"), dest_edge.encode("ascii"), length=float(edges_length[source_edge]), weight=0, congested = 0, speed = edges_speed[source_edge])
        

    return graph    

def gen_canditates_reroute(graph, congested_roads, level):
    reverseGraph = graph
    vehicles_reroute = set()
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
                        vehicles_reroute.add(vehicle)
    
    
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
  