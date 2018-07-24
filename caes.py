from pyomo.environ import (ConcreteModel, Set, Param, Var, Constraint,
                           Objective, Binary)
from pyomo.environ import maximize
from pyomo.opt import SolverFactory


# Data
T = [1, 2, 3, 4]
Cel = [20, 20, 20, 20]
Pmax = [30, 30, 30, 30]


# Create model
m = ConcreteModel()

# Sets
m.T = Set(initialize=T)

# Params (loop over dict and work with setattr?)
m.a = Param(m.T, initialize=a)
m.b = Param(m.T, initialize=b)
m.c = Param(m.T, initialize=c)
m.d = Param(m.T, initialize=d)
m.m_0 = Param(m.T, initialize=m_0)
m.Eta_ex = Param(m.T, initialize=Eta_ex)
m.exp_q_in_R = Param(m.T, initialize=exp_q_in_R)
m.exp_q_in_T_0 = Param(m.T, initialize=exp_q_in_T_0)
m.exp_q_in_cp = Param(m.T, initialize=exp_q_in_cp)
m.cav_Pi_min =  Param(m.T, initialize=cav_Pi_min)
m.cmp_P_max = Param(m.T, initialize=cmp_P_max)
m.cmp_P_min = Param(m.T, initialize=cmp_P_min)
m.exp_P_max = Param(m.T, initialize=exp_P_max)
m.exp_P_min = Param(m.T, initialize=exp_P_min)


m.C_el = Param(m.T, initialize=dict(zip(T, Cel)))


# Variables
m.P = Var(m.T, bounds=(0, 100))

# Constraints
def max_rule(model, t):
    return(m.P[t] >= m.Pmax[t])
m.max = Constraint(m.T, rule=max_rule)


# Objective
def obj_rule(model):
    return(sum(m.Cel[t]*m.P[t] for t in m.T))
m.profit = Objective(sense=maximize, rule=obj_rule)

# m.pprint()

# Define Solver
opt = SolverFactory('gurobi')

# Solve the model
results = opt.solve(m, tee=False)

# # Load results back into model
m.solutions.load_from(results)

# Print results
print([m.P[t].value for t in T])
