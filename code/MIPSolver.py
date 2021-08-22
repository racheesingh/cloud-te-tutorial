
class MIPSolver:

    def Variable(self, type):
        return None

    def Assert(self, constraint):
        pass

    def Maximize(self, objective):
        pass

    def Solve(self):
        pass

    def Value(self, variable):
        return None
    

import cvxpy as cp

class CvxSolver(MIPSolver):
    def __init__(self):
        self.constraints = []
        self.objective = None
        self.problem = None

    def Variable(self, type = None):
        if type == "Int":
            return cp.Variable(integer = True)            
        if type == "Bool":
            return cp.Variable(boolean = True)
        return cp.Variable(1)        

    def Maximize(self, objective):
        self.objective = cp.Maximize(objective)

    def Assert(self, constraint):
        self.constraints.append(constraint)

    def Solve(self):
        assert self.objective
        prob = cp.Problem(self.objective, self.constraints)
        self.problem = prob
        return  prob.solve()

    def Value(self, var):
        return var.value

    def __repr__(self):
        return ""
