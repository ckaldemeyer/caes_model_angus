"""Simple test model for Compressed Air Energy Storages (CAES)."""

import numpy as np
import pandas as pd
import rules as ru
import pyomo.environ as po
import matplotlib.pyplot as plt
from pyomo.opt import SolverFactory

# -----------------------------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------------------------
sca = pd.read_csv(
    'scalars_huntorf.csv', index_col=0)['value'].astype(np.float64).to_dict()
seq = pd.read_csv(
    'sequences_huntorf.csv', index_col=0).astype(np.float64).loc[0:24*4]

# -----------------------------------------------------------------------------
# CREATE MODEL
# -----------------------------------------------------------------------------
m = po.ConcreteModel()

# -----------------------------------------------------------------------------
# ADD SETS
# -----------------------------------------------------------------------------
m.T = po.Set(initialize=seq.index.values)

# -----------------------------------------------------------------------------
# ADD PARAMETERS
# -----------------------------------------------------------------------------
m.a0 = po.Param(initialize=sca['a0'])
m.a = po.Param(initialize=sca['a'])
m.b = po.Param(initialize=sca['b'])
m.c1 = po.Param(initialize=sca['c1'])
m.c2 = po.Param(initialize=sca['c2'])
m.cav_m_0 = po.Param(initialize=sca['cav_m_0'])
m.cmp_P_max = po.Param(initialize=sca['cmp_P_max'])
m.cmp_P_min = po.Param(initialize=sca['cmp_P_min'])
m.exp_P_max = po.Param(initialize=sca['exp_P_max'])
m.exp_P_min = po.Param(initialize=sca['exp_P_min'])
m.cav_Pi_o_0 = po.Param(initialize=sca['cav_Pi_o_0'])
m.cav_Pi_min = po.Param(initialize=sca['cav_Pi_min'])
m.cav_Pi_o_min = po.Param(initialize=sca['cav_Pi_o_min'])
m.cav_Pi_o_max = po.Param(initialize=sca['cav_Pi_o_max'])
m.mkt_C_el_cmp = po.Param(m.T, initialize=dict(zip(seq.index.values,
                                               seq['mkt_C_el_cmp'].values)))
m.mkt_C_el_exp = po.Param(m.T, initialize=dict(zip(seq.index.values,
                                               seq['mkt_C_el_exp'].values)))
m.mkt_C_fuel = po.Param(m.T, initialize=dict(zip(seq.index.values,
                                                 seq['mkt_C_fuel'].values)))
m.eta = po.Param(initialize=sca['eta'])

# -----------------------------------------------------------------------------
# ADD VARIABLES
# -----------------------------------------------------------------------------
m.cmp_P = po.Var(m.T, domain=po.NonNegativeReals,
                 bounds=(0, sca['cmp_P_max']))
m.cmp_y = po.Var(m.T, domain=po.Binary)
m.cmp_m = po.Var(m.T, domain=po.NonNegativeReals)
m.cmp_z = po.Var(m.T, domain=po.NonNegativeReals)
m.exp_P = po.Var(m.T, domain=po.NonNegativeReals,
                 bounds=(0, sca['exp_P_max']))
m.exp_y = po.Var(m.T, domain=po.Binary)
m.exp_m = po.Var(m.T, domain=po.NonNegativeReals)
m.exp_Q = po.Var(m.T, domain=po.NonNegativeReals)
m.cav_Pi_o = po.Var(m.T, domain=po.NonNegativeReals,
                    bounds=(sca['cav_Pi_o_min'],
                            sca['cav_Pi_o_max']))

# -----------------------------------------------------------------------------
# ADD OBJECTIVE
# -----------------------------------------------------------------------------
m.profit = po.Objective(sense=po.minimize, rule=ru.profit)

# -----------------------------------------------------------------------------
# ADD CONSTRAINTS
# -----------------------------------------------------------------------------
m.cav_pi = po.Constraint(m.T, rule=ru.cav_pi)
m.cav_pi_t0 = po.Constraint(m.T, rule=ru.cav_pi_t0)
# m.cav_pi_tmax = po.Constraint(m.T, rule=ru.cav_pi_tmax)
m.cmp_z1 = po.Constraint(m.T, rule=ru.cmp_z1)
m.cmp_z2 = po.Constraint(m.T, rule=ru.cmp_z2)
m.cmp_z3 = po.Constraint(m.T, rule=ru.cmp_z3)
m.cmp_z4 = po.Constraint(m.T, rule=ru.cmp_z4)
m.cmp_area = po.Constraint(m.T, rule=ru.cmp_area)
m.cmp_p_range_min = po.Constraint(m.T, rule=ru.cmp_p_range_min)
m.cmp_p_range_max = po.Constraint(m.T, rule=ru.cmp_p_range_max)
m.exp_area1 = po.Constraint(m.T, rule=ru.exp_area1)
m.exp_area2 = po.Constraint(m.T, rule=ru.exp_area2)
m.exp_p_range_min = po.Constraint(m.T, rule=ru.exp_p_range_min)
m.exp_p_range_max = po.Constraint(m.T, rule=ru.exp_p_range_max)
m.cmp_exp_excl = po.Constraint(m.T, rule=ru.cmp_exp_excl)

# -----------------------------------------------------------------------------
# SOLVE AND SAVE RESULTS
# -----------------------------------------------------------------------------
opt = SolverFactory('gurobi')
results = opt.solve(m, tee=False)

# -----------------------------------------------------------------------------
# PROCESS RESULTS
# -----------------------------------------------------------------------------
m.solutions.load_from(results)

data = {'C_el_cmp': seq['mkt_C_el_cmp'].values,
        'C_el_exp': seq['mkt_C_el_exp'].values,
        'cmp_P': [m.cmp_P[t].value for t in m.T],
        'cmp_y': [m.cmp_y[t].value for t in m.T],
        'exp_P': [m.exp_P[t].value for t in m.T],
        'exp_y': [m.exp_y[t].value for t in m.T],
        'exp_Q': [m.exp_Q[t].value for t in m.T],
        'cav_Pi_o': [m.cav_Pi_o[t].value for t in m.T],
        'cmp_m': [m.cmp_m[t].value for t in m.T],
        'exp_m': [m.exp_m[t].value for t in m.T]}

df = pd.DataFrame.from_dict(data)
df.sort_index(axis=1, inplace=True)

print('Objective: ', m.profit())
print(df.sum())

# -----------------------------------------------------------------------------
# PLOT RESULTS
# -----------------------------------------------------------------------------
# columns = ['cmp_P', 'cmp_m', 'exp_P', 'exp_m', 'cav_Pi_o']
columns = ['C_el_cmp', 'C_el_exp', 'cmp_P', 'exp_P', 'cav_Pi_o']
df[columns].plot(kind='line', drawstyle='steps-post', subplots=True, grid=True)
plt.tight_layout()
plt.show()
