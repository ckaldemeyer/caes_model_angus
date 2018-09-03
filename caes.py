"""Generic model for diabatic Compressed Air Energy Storages (CAES)."""

import numpy as np
import pandas as pd
import rules as ru
import pyomo.environ as po
import matplotlib.pyplot as plt
from pyomo.opt import SolverFactory


# Load data
sca = pd.read_csv(
    'scalars_huntorf.csv', index_col=0)['value'].astype(np.float64).to_dict()
seq = pd.read_csv(
    'sequences_huntorf.csv', index_col=0).astype(np.float64).loc[0:24*4]

# Create model
m = po.ConcreteModel()

# Add sets
m.T = po.Set(initialize=seq.index.values)

# Add parameters
m.cmp_P_max = po.Param(initialize=sca['cmp_P_max'])
m.cmp_P_min = po.Param(initialize=sca['cmp_P_min'])
m.cmp_a = po.Param(initialize=sca['cmp_a'])
m.cmp_b = po.Param(initialize=sca['cmp_b'])
m.cmp_c = po.Param(initialize=sca['cmp_c'])
m.cmp_d = po.Param(initialize=sca['cmp_d'])
m.cmp_eta = po.Param(initialize=sca['cmp_eta'])
m.cas_m_0 = po.Param(initialize=sca['cas_m_0'])
m.cas_Pi_o_0 = po.Param(initialize=sca['cas_Pi_o_0'])
m.cas_Pi_min = po.Param(initialize=sca['cas_Pi_min'])
m.cas_Pi_o_max = po.Param(initialize=sca['cas_Pi_o_max'])
m.exp_P_max = po.Param(initialize=sca['exp_P_max'])
m.exp_P_min = po.Param(initialize=sca['exp_P_min'])
m.exp_a = po.Param(initialize=sca['exp_a'])
m.exp_b = po.Param(initialize=sca['exp_b'])
m.mkt_C_el_cmp = po.Param(m.T, initialize=dict(zip(seq.index.values,
                                               seq['mkt_C_el_cmp'].values)))
m.mkt_C_el_exp = po.Param(m.T, initialize=dict(zip(seq.index.values,
                                               seq['mkt_C_el_exp'].values)))
m.mkt_C_fuel = po.Param(m.T, initialize=dict(zip(seq.index.values,
                                                 seq['mkt_C_fuel'].values)))

# Add variables
m.cmp_P = po.Var(m.T, domain=po.NonNegativeReals,
                 bounds=(0, sca['cmp_P_max']))
m.cmp_Q = po.Var(m.T, domain=po.NonNegativeReals)
m.cmp_y = po.Var(m.T, domain=po.Binary)
m.cmp_m = po.Var(m.T, domain=po.NonNegativeReals)
m.cmp_z = po.Var(m.T, domain=po.NonNegativeReals)
m.cas_Pi_o = po.Var(m.T, domain=po.NonNegativeReals,
                    bounds=(0, sca['cas_Pi_o_max']))
m.exp_P = po.Var(m.T, domain=po.NonNegativeReals,
                 bounds=(0, sca['exp_P_max']))
m.exp_y = po.Var(m.T, domain=po.Binary)
m.exp_m = po.Var(m.T, domain=po.NonNegativeReals)
m.exp_Q = po.Var(m.T, domain=po.NonNegativeReals)

# Add objective
m.profit = po.Objective(sense=po.minimize, rule=ru.profit)

# Add constraints
m.cmp_p_range_min = po.Constraint(m.T, rule=ru.cmp_p_range_min)
m.cmp_p_range_max = po.Constraint(m.T, rule=ru.cmp_p_range_max)
m.cmp_area1 = po.Constraint(m.T, rule=ru.cmp_area1)
m.cmp_area2 = po.Constraint(m.T, rule=ru.cmp_area2)
m.cmp_z1 = po.Constraint(m.T, rule=ru.cmp_z1)
m.cmp_z2 = po.Constraint(m.T, rule=ru.cmp_z2)
m.cmp_z3 = po.Constraint(m.T, rule=ru.cmp_z3)
m.cmp_z4 = po.Constraint(m.T, rule=ru.cmp_z4)
m.cas_pi = po.Constraint(m.T, rule=ru.cas_pi)
m.cas_pi_t0 = po.Constraint(m.T, rule=ru.cas_pi_t0)
m.cas_pi_tmax = po.Constraint(m.T, rule=ru.cas_pi_tmax)
m.exp_p_range_min = po.Constraint(m.T, rule=ru.exp_p_range_min)
m.exp_p_range_max = po.Constraint(m.T, rule=ru.exp_p_range_max)
m.exp_area1 = po.Constraint(m.T, rule=ru.exp_area1)
m.exp_area2 = po.Constraint(m.T, rule=ru.exp_area2)
m.cmp_exp_excl = po.Constraint(m.T, rule=ru.cmp_exp_excl)

# Solve and save results
opt = SolverFactory('gurobi')
results = opt.solve(m, tee=False)

# Process results
m.solutions.load_from(results)
data = {'C_el_cmp': seq['mkt_C_el_cmp'].values,
        'C_el_exp': seq['mkt_C_el_exp'].values,
        'cmp_P': [m.cmp_P[t].value for t in m.T],
        'cmp_Q': [m.cmp_Q[t].value for t in m.T],
        'cmp_y': [m.cmp_y[t].value for t in m.T],
        'exp_P': [m.exp_P[t].value for t in m.T],
        'exp_y': [m.exp_y[t].value for t in m.T],
        'exp_Q': [m.exp_Q[t].value for t in m.T],
        'cas_Pi_o': [m.cas_Pi_o[t].value for t in m.T],
        'cmp_m': [m.cmp_m[t].value for t in m.T],
        'exp_m': [m.exp_m[t].value for t in m.T]}
df = pd.DataFrame.from_dict(data)
df.sort_index(axis=1, inplace=True)
print('Objective: ', m.profit())
print(df.sum())

# Plot results
columns = ['C_el_cmp', 'C_el_exp', 'cmp_P', 'cmp_Q', 'exp_P', 'cas_Pi_o']
df[columns].plot(kind='line', drawstyle='steps-post', subplots=True, grid=True)
plt.tight_layout()
plt.show()
