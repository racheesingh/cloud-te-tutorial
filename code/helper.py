import networkx as nx

def get_max_flow_objective(network):
    """sum of all flows in all tunnels
    """
    return sum([t.v_flow for t in network.tunnels.values()])

def get_max_flow_min_weight_objective(network, epsilon=0.01):
    """sum of all flows in all tunnels penalized for weight
    each tunnel flow is reward with 1 - tunnel weight*epsilon
    """
    def reward(tunnel):
        return (1 - epsilon * tunnel.weight) * tunnel.v_flow
    return sum([reward(t) for t in network.tunnels.values()])

def get_ffc_objective(network):
    return sum([demand.b_d for demand in network.demands.values()])

def get_wavelength_objective(network):
    objective = 0
    for shortcut in network.shortcuts.values():
        objective += (len(shortcut.path) -1 )* shortcut.w_s
    return objective

def get_edge_flow_allocations(network):
    """ 
    Get the optimal edge allocations.
    """
    flow_labels = {}
    for edge in network.edges.values():
        allocation = 0
        for tunnel in edge.tunnels:
            allocation += tunnel.v_flow.value
        flow_labels[edge.e] = round(allocation[0], 2)
    return flow_labels

def get_demands_met(network):
    demands_met = {}
    for demand in network.demands.values():
        flow_on_tunnels = sum([tunnel.v_flow.value for tunnel in demand.tunnels])
        demands_met[(demand.src, demand.dst)] = flow_on_tunnels[0]
    return demands_met

def get_demands_unmet(network):
    demands_met = {}
    for demand in network.demands.values():
        flow_on_tunnels = sum([tunnel.v_flow.value for tunnel in demand.tunnels])
        demands_met[(demand.src, demand.dst)] = round(demand.amount - flow_on_tunnels[0])
    return demands_met

def shortest_path_by_distance(G, v1, v2, nhops):
    sp_list = nx.all_shortest_paths(G, v1, v2)
    shortest_path_to_distance = {}
    for sp in sp_list:
        if len(sp) > nhops: continue
        sp_str = ':'.join(sp)
        sp_distance = 0
        for node1, node2 in zip(sp, sp[1:]):
            sp_distance += G[node1][node2]["distance"]

        assert sp_distance > 0
        shortest_path_to_distance[sp_str] = sp_distance
        
    if not shortest_path_to_distance: return None, None
    sorted_sps = sorted(shortest_path_to_distance.items(), key=lambda x:x[1])
    return sorted_sps[0][0], sorted_sps[0][1]

def unity_from_distance(shortcut_distance):
    if shortcut_distance <= 800:
        unity = 200
    elif shortcut_distance <= 2500:
        unity = 150
    elif shortcut_distance <= 5000:
        unity = 100
    else:
        unity = 0
    return unity

def get_viable_failures(network, k=1):
    """
    Returns the set of edge tuples that can fail.
    """
    return []

