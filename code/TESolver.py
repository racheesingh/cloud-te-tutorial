import pdb
class TESolver:
    def __init__(self, mip, network):
        self.mip = mip
        self.network = network
        self.initialize_optimization_variables()
        
    def initialize_optimization_variables(self):
        for tunnel in self.network.tunnels.values():
            tunnel.init_flow_var(self.mip)
        
    def add_demand_constraints(self):
        for demand in self.network.demands.values():
            flow_on_tunnels = sum([tunnel.v_flow for tunnel in demand.tunnels])
            assert len(demand.tunnels) > 0
            self.mip.Assert(demand.amount >= flow_on_tunnels)

    def add_edge_capacity_constraints(self):
        for edge_pair in self.network.edges:
            edge = self.network.edges[edge_pair]
            self.mip.Assert(edge.capacity >= sum(t.v_flow for t in edge.tunnels))
                    
                    
    def Maximize(self, objective):
        self.mip.Maximize(objective)
        
    def solve(self):
        return self.mip.Solve()


class FFCSolver(TESolver):
    def __init__(self, mip, network):
        TESolver.__init__(self, mip, network)
            
        for demand in self.network.demands.values():
            demand.init_b_d(self.mip)
        
    def failure_scenario_edge_constraint(self, alpha):

        def tunnel_alpha(tunnel):
            return 0 if any(set(alpha) & set(tunnel.path)) else 1

        for demand in self.network.demands.values():
            flow_on_tunnels = sum([tunnel_alpha(t) * t.v_flow for t in demand.tunnels])
            self.mip.Assert(demand.b_d <= flow_on_tunnels)
                            
    def add_demand_constraints(self):
        for demand in self.network.demands.values():
            self.mip.Assert(demand.b_d <= demand.amount)
            
    def pairwise_failures(self):
        return itertools.combinations(self.network.edges.values(), r = 2)

    def add_edge_capacity_constraints(self):
        for edge in self.network.edges.values():
            allocation = 0
            for tunnel in edge.tunnels:
                allocation += tunnel.v_flow                
            self.mip.Assert(edge.capacity >= allocation)

                                      
class DualFFCSolver(TESolver):
    def __init__(self, mip, network, k):
        TESolver.__init__(self, mip, network)

        for demand in self.network.demands.values():
            demand.init_b_d(self.mip)
            self.init_dual(demand, k)            
    
    def init_dual(self, demand, k):
        vars = {}
        
        def y(x):
            if x not in vars:
                vars[x] = self.mip.Variable()
                self.mip.Assert(vars[x] >= 0)
            return vars[x]
        
        def f(t):
            return t.v_flow
        
        yf = self.mip.Variable()
        self.mip.Assert(yf >= 0)
        
        def edges(t):
            return t.path
        
        demand_edges = { e for t in demand.tunnels for e in t.path }
        dual_sum = (len(demand_edges) - k)*yf - \
                   sum(y(e) for e in demand_edges) + \
                sum((1 - len(edges(t)))*y(t) for t in demand.tunnels)
        self.mip.Assert(demand.b_d <= dual_sum)
        
        for t in demand.tunnels:
            self.mip.Assert(y(t) - sum(y((e, t)) for e in t.path)  <= t.v_flow)
            
        for e in demand_edges:
            self.mip.Assert(sum(y((e,t)) - y(t) for t in demand.tunnels if e in t.path) - \
                            y(e) + yf <= 0)
        self.mip.Assert(demand.b_d <= demand.amount)

    def add_edge_capacity_constraints(self):
        for edge in self.network.edges.values():
            allocation = 0
            for tunnel in edge.tunnels:
                allocation += tunnel.v_flow                
            self.mip.Assert(edge.capacity >= allocation)
        
class ShooflySolver(TESolver):
    def __init__(self, mip, network):
        TESolver.__init__(self, mip, network)
        for edge in self.network.edges.values():
            edge.init_x_e_vars(self.mip)        
        # Initialize shortcuts
        self.network.init_shortcuts()
        for shortcut in network.shortcuts.values():
            # wavelengths on shortcuts
            shortcut.init_wavelength_vars(self.mip)
            # flow allocation on the shortcuts
            shortcut.init_y_s_vars(self.mip)
        
    def add_wavelength_integrality_constraints(self):
        for shortcut in self.network.shortcuts.values():
            y_s_all_tunnels = sum([shortcut.y_s[tunnel] for tunnel in shortcut.tunnels])
            self.mip.Assert(y_s_all_tunnels <= shortcut.w_s * shortcut.unity)

    def add_complementary_shortcut_constraints(self):
        for shortcut_pair in self.network.shortcut_node_pairs:
            shortcut_obj = self.network.shortcut_node_pairs[shortcut_pair]
            shortcut_obj_complementary = self.network.shortcut_node_pairs[
                (shortcut_pair[1], shortcut_pair[0])]
            self.mip.Assert(shortcut_obj.w_s == shortcut_obj_complementary.w_s)
            
    def add_flow_conservation_constraints(self):
        for edge in self.network.edges.values():
            for tunnel in edge.tunnels:
                x_e_t = edge.x_e_t[tunnel]
                y_s_t_sum = sum([shortcut.y_s[tunnel] for shortcut in edge.shortcuts
                                 if tunnel in shortcut.tunnels])
                self.mip.Assert(tunnel.v_flow <= x_e_t + y_s_t_sum)
            
    def add_demand_constraints(self):
        for demand in self.network.demands.values():
            flow_on_tunnels = sum([tunnel.v_flow for tunnel in demand.tunnels])
            assert len(demand.tunnels) > 0
            self.mip.Assert(demand.amount <= flow_on_tunnels)
                        
    def add_edge_capacity_constraints(self):
        for edge_pair in self.network.edges:
            edge = self.network.edges[edge_pair]
            x_e = sum(edge.x_e_t.values())
            w_s = sum([shortcut.w_s for shortcut in edge.shortcuts])
            self.mip.Assert(edge.capacity >= x_e + edge.unity*w_s)
