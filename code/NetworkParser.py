import random
from NetworkTopology import *
import csv

def parse_topology(network_name):
    network = Network(network_name)
    with open(f"data/{network_name}/topology.txt") as fi:
        reader = csv.reader(fi, delimiter=" ")
        for row_ in reader:
            if row_[0] == 'to_node': continue
            row = [x for x in row_ if x]
            to_node = row[0]
            from_node = row[1]
            capacity = int(float(row[2])/1000.0)
            network.add_node(to_node, None, None)
            network.add_node(from_node, None, None)
            network.add_edge(from_node, to_node, 200, capacity)            
    return network

def parse_demands(network, scale=1):
    network_name = network.name
    num_nodes = len(network.nodes)
    demand_matrix = {}
    with open(f"data/{network_name}/demand.txt") as fi:
        reader = csv.reader(fi, delimiter=" ")
        for row_ in reader:
            if row_[0] == 'to_node': continue
            row = [float(x) for x in row_ if x]
            assert len(row) == num_nodes ** 2
            for idx, dem in enumerate(row):
                from_node = int(idx/num_nodes) + 1
                to_node = idx % num_nodes + 1
                assert str(from_node) in network.nodes
                assert str(to_node) in network.nodes
                if from_node not in demand_matrix:
                    demand_matrix[from_node] = {}
                if to_node not in demand_matrix[from_node]:
                    demand_matrix[from_node][to_node] = []
                demand_matrix[from_node][to_node].append(dem/1000.0)
        for from_node in demand_matrix:
            for to_node in demand_matrix[from_node]:
                max_demand = max(demand_matrix[from_node][to_node])
                network.add_demand(str(from_node), str(to_node), max_demand, scale)
    if network.tunnels:
        remove_demands_without_tunnels(network)

def parse_tunnels(network):
    # Parse tunnels
    for node1 in network.nodes:
        for node2 in network.nodes:
            if node1 == node2: continue
            paths = network.k_shortest_paths(node1, node2, 5)
            for path in paths:
                tunnel = network.add_tunnel(path)
    if network.demands:
        remove_demands_without_tunnels(network)

def remove_demands_without_tunnels(network):
    removable_demands = [p for p, d in network.demands.items() if not d.tunnels]
    for demand_pair in removable_demands:
        del network.demands[demand_pair]

def initialize_weights(network):
    for tunnel in network.tunnels.values():
        tunnel.add_weight(random.randint(1, 10))
        
