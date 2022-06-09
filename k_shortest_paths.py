# -*- coding: utf-8 -*-


__all__ = ['k_shortest_paths']

from heapq import heappush, heappop
from itertools import count

import networkx as nx

def k_shortest_paths(G, source, target, k, weight='weight'):
    if source == target:
        return ([0], [[source]]) 
       
    length, path = nx.single_source_dijkstra(G, source, target, weight=weight)
    # length, path = nx.bidirectional_dijkstra(G, source, target, weight=weight)
    # print('p1: ', path)

    if target not in length:
        raise nx.NetworkXNoPath("node %s not reachable from %s" % (source, target))
        
    lengths = [length[target]]
    paths = [path[target]]
    c = count()        
    B = []                        
    G_original = G.copy()    
    
    for i in range(1, k):
        # print('i: ',i)
        for j in range(len(paths[-1]) - 1):            
            spur_node = paths[-1][j]
            root_path = paths[-1][:j + 1]
            
            edges_removed = []
            for c_path in paths:
                if len(c_path) > j and root_path == c_path[:j + 1]:
                    u = c_path[j]
                    v = c_path[j + 1]
                    if G.has_edge(u, v):
                        edge_attr = G.edge[u][v]
                        G.remove_edge(u, v)
                        edges_removed.append((u, v, edge_attr))
            
            for n in range(len(root_path) - 1):
                node = root_path[n]
                # out-edges
                for u, v, edge_attr in G.edges_iter(node, data=True):
                    G.remove_edge(u, v)
                    edges_removed.append((u, v, edge_attr))

                if G.is_directed():
                    # in-edges
                    for u, v, edge_attr in G.in_edges_iter(node, data=True):
                        G.remove_edge(u, v)
                        edges_removed.append((u, v, edge_attr))

            # spur_path_length, spur_path = nx.bidirectional_dijkstra(G, spur_node, target, weight=weight)
            spur_path_length, spur_path = nx.single_source_dijkstra(G, spur_node, target, weight=weight)
            # print('p:',i, spur_path)
            if target in spur_path and spur_path[target]:
                total_path = root_path[:-1] + spur_path[target]
                total_path_length = get_path_length(G_original, root_path, weight) + spur_path_length[target]                
                heappush(B, (total_path_length, next(c), total_path))
                
            for e in edges_removed:
                # print ('Rem: ', e)
                u, v, edge_attr = e
                G.add_edge(u, v, edge_attr)
                       
        if B:
            (l, _, p) = heappop(B)        
            lengths.append(l)
            paths.append(p)
        else:
            break
    
    return (lengths, paths)

def get_path_length(G, path, weight='weight'):
    length = 0
    if len(path) > 1:
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]
            
            length += G.edge[u][v].get(weight, 1)
    
    return length    
