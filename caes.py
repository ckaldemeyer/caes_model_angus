import pandas as pd
from pyomo.environ import *
from pyomo.opt import SolverFactory


# Load data
sca = pd.read_csv('scalars.csv', index_col=0)
seq = pd.read_csv('sequences.csv')

# Create model
m = ConcreteModel()

# Add sets
m.T = Set(initialize=seq['timestep'].values)

# Add parameters
m.a = Param(m.T, initialize=sca.loc['a'].item())
m.b = Param(m.T, initialize=sca.loc['b'].item())
m.c = Param(m.T, initialize=sca.loc['c'].item())
m.d = Param(m.T, initialize=sca.loc['d'].item())
m.cmp_P_max = Param(m.T, initialize=sca.loc['cmp_P_max'].item())
m.cmp_P_min = Param(m.T, initialize=sca.loc['cmp_P_min'].item())
m.exp_P_max = Param(m.T, initialize=sca.loc['exp_P_max'].item())
m.exp_P_min = Param(m.T, initialize=sca.loc['exp_P_min'].item())
m.exp_Eta_ex = Param(m.T, initialize=sca.loc['exp_Eta_ex'].item())
m.exp_T_0 = Param(m.T, initialize=sca.loc['exp_T_0'].item())
m.exp_R = Param(m.T, initialize=sca.loc['exp_R'].item())
m.exp_ln = Param(m.T, initialize=sca.loc['exp_ln'].item())
m.exp_cp = Param(m.T, initialize=sca.loc['exp_cp'].item())
m.exp_Delta_T = Param(m.T, initialize=sca.loc['exp_Delta_T'].item())
m.exp_Eta_comb = Param(m.T, initialize=sca.loc['exp_Eta_comb'].item())
m.cav_m_0 = Param(m.T, initialize=sca.loc['cav_m_0'].item())
m.cav_Pi_min = Param(m.T, initialize=sca.loc['cav_Pi_min'].item())
m.cav_Pi_max = Param(m.T, initialize=sca.loc['cav_Pi_max'].item())
m.mkt_C_el = Param(m.T, initialize=dict(zip(seq['timestep'].values,
                                            seq['mkt_C_el'].values)))

# Add variables
m.cmp_P = Var(m.T, domain=NonNegativeReals,
              bounds=(0, sca.loc['cmp_P_max'].item()))
m.cmp_m = Var(m.T, domain=NonNegativeReals)
m.cmp_y = Var(m.T, domain=Binary)
m.exp_Q = Var(m.T, domain=NonNegativeReals,
              bounds=(0, sca.loc['exp_max'].item()))
m.exp_m = Var(m.T, domain=NonNegativeReals)
m.exp_y = Var(m.T, domain=Binary)
m.cav_Pi = Var(m.T, domain=NonNegativeReals,
               bounds=(sca.loc['cav_Pi_min'].item(),
                       sca.loc['cav_Pi_max'].item()))


# Add objective
def obj_rule(model):
    expr = (sum(m.mkt_C_el[t] * m.cmp_P[t] +
            m.mkt_C_fuel[t] * m.exp_Q_in[t] -
            m.mkt_C_el[t] * m.exp_P[t]
            for t in m.T))
    return expr
m.profit = Objective(sense=minimize, rule=obj_rule)


# Add constraints
def cmp_area_rule(model, t):
    return(m.cmp_P[t] == m.a * m.cmp_m[t] + m.b * m.cav_Pi[t])
m.cmp_area = Constraint(m.T, rule=cmp_area_rule)


def cav_pi_rule(model, t):
    return(m.cav_Pi[t] == m.cav_Pi[t] + 1/m.cav_m_0 * (m.cmp_m[t] - m.exp_m[t]))
m.cav_pi = Constraint(m.T, rule=cav_pi_rule)


def exp_area_rule(model, t):
    return(m.exp_P[t] == m.c * m.exp_m[t] + m.d * m.cav_Pi[t])
m.cmp_area = Constraint(m.T, rule=cmp_area_rule)


def cmp_p_range_rule_1(model, t):
    return(m.cmp_P[t] <= m.cmp_y[t] * m.cmp_P_max[t])
m.cmp_p_range_1 = Constraint(m.T, rule=cmp_p_range_rule_1)


def cmp_p_range_rule_2(model, t):
    return(m.cmp_y[t] * m.cmp_P_max[t] >= m.cmp_P[t])
m.cmp_p_range_2 = Constraint(m.T, rule=cmp_p_range_rule_2)


def exp_p_range_rule_1(model, t):
    return(m.exp_P[t] <= m.exp_y[t] * m.exp_P_max[t])
m.exp_p_range_1 = Constraint(m.T, rule=exp_p_range_rule_1)


def exp_p_range_rule_2(model, t):
    return(m.exp_y[t] * m.exp_P_max[t] >= m.exp_P[t])
m.exp_p_range_2 = Constraint(m.T, rule=exp_p_range_rule_2)


def cmp_exp_excl_rule(model, t):
    return(m.cmp_y[t] + m.exp_y[t] <= 1)
m.cmp_exp_excl = Constraint(m.T, rule=cmp_exp_excl_rule)


# def exp_fuel_rule_1(model, t):
#     return(m.exp_Q[t] == m.exp_P[t] / m.exp_Eta_ex -
#            m.exp_m[t] * m.exp_T_0 * m.exp_R * m.exp_ln)
# m.exp_fuel_1 = Constraint(m.T, rule=exp_fuel_rule_1)


def exp_fuel_rule_2(model, t):
    return(m.exp_Q[t] == m.exp_m[t] * m.exp_cp *
           m.exp_delta_T / m.exp_Eta_comb)
m.exp_fuel_2 = Constraint(m.T, rule=exp_fuel_rule_2)


# Set solver
opt = SolverFactory('gurobi')

# Solve model
results = opt.solve(m, tee=False)

# Load results back into model
m.solutions.load_from(results)

# Print results
data = {'cmp_P': [m.cmp_P[t].value for t in m.T],
        'exp_P': [m.exp_P[t].value for t in m.T],
        'cav_Pi': [m.cav_Pi[t].value for t in m.T]}
df = pd.DataFrame.from_dict(data)

print(df.head(24))
