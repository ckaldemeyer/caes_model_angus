"""Simple test model for Compressed Air Energy Storages (CAES)."""

import numpy as np
import pandas as pd
import rules as ru
import pyomo.environ as po
import matplotlib.pyplot as plt
from pyomo.opt import SolverFactory


# Load data
sca = pd.read_csv('scalars.csv', index_col=0).astype(np.float64)['value']
seq = pd.read_csv('sequences.csv', index_col=0).astype(np.float64).loc[1:24]

# Create model
m = po.ConcreteModel()

# Add sets
m.T = po.Set(initialize=seq.index.values)

# Add parameters
m.a0 = po.Param(initialize=sca.loc['a0'].item())
m.a = po.Param(initialize=sca.loc['a'].item())
m.b = po.Param(initialize=sca.loc['b'].item())
m.c1 = po.Param(initialize=sca.loc['c1'].item())
m.c2 = po.Param(initialize=sca.loc['c2'].item())
m.cmp_P_max = po.Param(initialize=sca.loc['cmp_P_max'].item())
m.cmp_P_min = po.Param(initialize=sca.loc['cmp_P_min'].item())
m.exp_P_max = po.Param(initialize=sca.loc['exp_P_max'].item())
m.exp_P_min = po.Param(initialize=sca.loc['exp_P_min'].item())
m.cav_m_0 = po.Param(initialize=sca.loc['cav_m_0'].item())
m.cav_Pi_0 = po.Param(initialize=sca.loc['cav_Pi_0'].item())
m.cav_Pi_min = po.Param(initialize=sca.loc['cav_Pi_min'].item())
m.cav_Pi_max = po.Param(initialize=sca.loc['cav_Pi_max'].item())
m.cav_Pi_o_min = po.Param(initialize=sca.loc['cav_Pi_o_min'].item())
m.cav_Pi_o_max = po.Param(initialize=sca.loc['cav_Pi_o_max'].item())
m.mkt_C_el = po.Param(m.T, initialize=dict(zip(seq.index.values,
                                               seq['mkt_C_el'].values)))
m.mkt_C_fuel = po.Param(m.T, initialize=dict(zip(seq.index.values,
                                                 seq['mkt_C_fuel'].values)))


# Add variables
m.cmp_P = po.Var(m.T, domain=po.NonNegativeReals,
                 bounds=(0, sca.loc['cmp_P_max'].item()))
m.cmp_y = po.Var(m.T, domain=po.Binary)
m.cmp_m = po.Var(m.T, domain=po.NonNegativeReals)
m.cmp_z = po.Var(m.T, domain=po.NonNegativeReals)
m.exp_P = po.Var(m.T, domain=po.NonNegativeReals,
                 bounds=(0, sca.loc['exp_P_max'].item()))
m.exp_y = po.Var(m.T, domain=po.Binary)
m.exp_m = po.Var(m.T, domain=po.NonNegativeReals)
m.exp_Q = po.Var(m.T, domain=po.NonNegativeReals)
m.cav_Pi = po.Var(m.T, domain=po.NonNegativeReals,
                  bounds=(sca.loc['cav_Pi_min'].item(),
                          sca.loc['cav_Pi_max'].item()))
m.cav_Pi_o = po.Var(m.T, domain=po.NonNegativeReals,
                    bounds=(sca.loc['cav_Pi_o_min'].item(),
                            sca.loc['cav_Pi_o_max'].item()))


# Add objective
#m.profit = po.Objective(sense=po.minimize, rule=ru.obj)
m.profit_test = po.Objective(sense=po.minimize, rule=ru.obj_test)

# Add constraints
m.cav_pi = po.Constraint(m.T, rule=ru.cav_pi)
m.cmp_z1 = po.Constraint(m.T, rule=ru.cmp_z1)
m.cmp_z2 = po.Constraint(m.T, rule=ru.cmp_z2)
m.cmp_z3 = po.Constraint(m.T, rule=ru.cmp_z3)
m.cmp_area = po.Constraint(m.T, rule=ru.cmp_area)
m.cmp_p_range_min = po.Constraint(m.T, rule=ru.cmp_p_range_min)
m.cmp_p_range_max = po.Constraint(m.T, rule=ru.cmp_p_range_max)
m.exp_area1 = po.Constraint(m.T, rule=ru.exp_area1)
m.exp_area2 = po.Constraint(m.T, rule=ru.exp_area2)
m.exp_p_range_min = po.Constraint(m.T, rule=ru.exp_p_range_min)
m.exp_p_range_max = po.Constraint(m.T, rule=ru.exp_p_range_max)
m.cmp_exp_excl = po.Constraint(m.T, rule=ru.cmp_exp_excl)

# Print model (select only a few timesteps)
#m.pprint()

# Set solver
opt = SolverFactory('gurobi')

# Solve model
results = opt.solve(m, tee=False)

# Load results back into model
m.solutions.load_from(results)

# Print results
data = {'cmp_P': [m.cmp_P[t].value for t in m.T],
        'cmp_y': [m.cmp_y[t].value for t in m.T],
        'exp_P': [m.exp_P[t].value for t in m.T],
        'exp_y': [m.exp_y[t].value for t in m.T],
        'exp_Q': [m.exp_P[t].value for t in m.T],
        'cav_Pi': [m.cav_Pi[t].value for t in m.T],
        'cav_Pi_o': [m.cav_Pi_o[t].value for t in m.T],
        'cmp_m': [m.cmp_m[t].value for t in m.T],
        'exp_m': [m.exp_m[t].value for t in m.T]}
df = pd.DataFrame.from_dict(data)
df.sort_index(axis=1, inplace=True)

print(df)

# df.plot(kind='line', drawstyle='steps-post', subplots=True, grid=True)
# plt.tight_layout()
# plt.show()
