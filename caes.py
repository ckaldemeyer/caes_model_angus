import pandas as pd
from pyomo.environ import *
from pyomo.opt import SolverFactory


# Load data
sca = pd.read_csv('scalars.csv', index_col=0)
seq = pd.read_csv('sequences.csv')

# Create model
m = ConcreteModel()

# Sets
m.T = Set(initialize=seq['timestep'].values)

# Params
m.a = Param(m.T, initialize=sca.loc['a'].item())
m.b = Param(m.T, initialize=sca.loc['b'].item())
m.c = Param(m.T, initialize=sca.loc['c'].item())
m.d = Param(m.T, initialize=sca.loc['d'].item())
m.cmp_P_max = Param(m.T, initialize=sca.loc['cmp_P_max'].item())
m.cmp_P_min = Param(m.T, initialize=sca.loc['cmp_P_min'].item())
m.exp_P_max = Param(m.T, initialize=sca.loc['exp_P_max'].item())
m.exp_P_min = Param(m.T, initialize=sca.loc['exp_P_min'].item())
m.exp_q_in_Eta_ex = Param(m.T, initialize=sca.loc['exp_q_in_Eta_ex'].item())
m.exp_q_in_R = Param(m.T, initialize=sca.loc['exp_q_in_R'].item())
m.exp_q_in_T_0 = Param(m.T, initialize=sca.loc['exp_q_in_T_0'].item())
m.exp_q_in_cp = Param(m.T, initialize=sca.loc['exp_q_in_cp'].item())
m.cav_m_0 = Param(m.T, initialize=sca.loc['cav_m_0'].item())
m.cav_Pi_min = Param(m.T, initialize=sca.loc['cav_Pi_min'].item())
m.cav_Pi_max = Param(m.T, initialize=sca.loc['cav_Pi_max'].item())
m.mkt_C_el = Param(m.T, initialize=dict(
    zip(seq['timestep'].values, seq['mkt_C_el'].values)))

# Variables
m.P = Var(m.T, bounds=(0, 100))

# Objective
def obj_rule(model):
    return(sum(m.Cel[t]*m.P[t] for t in m.T))
m.profit = Objective(sense=maximize, rule=obj_rule)

# Constraints
def max_rule(model, t):
    return(m.P[t] >= m.Pmax[t])
m.max = Constraint(m.T, rule=max_rule)

# m.pprint()

# Define Solver
opt = SolverFactory('gurobi')

# Solve the model
results = opt.solve(m, tee=False)

# # Load results back into model
m.solutions.load_from(results)

# Print results
print([m.P[t].value for t in T])
