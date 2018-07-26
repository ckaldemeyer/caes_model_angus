"""Objective and constraint rules for Compressed Air Energy Storages (CAES)."""


# Add objective rules
def obj_rule(m):
    expr = (sum(m.mkt_C_el[t] * m.cmp_P[t] +
                m.mkt_C_fuel[t] * m.exp_Q[t] -
                m.mkt_C_el[t] * m.exp_P[t]
            for t in m.T))
    return expr


def obj_test_rule(m):
    expr = (sum(m.mkt_C_el[t] * m.cmp_P[t] -
                m.mkt_C_el[t] * m.exp_P[t]
            for t in m.T))
    return expr


# Add constraint rules
def cmp_area_rule(m, t):
    return(m.cmp_m[t] == (
        m.a0 + m.a * m.cmp_P[t] + m.b * m.cav_Pi[t]) * m.cmp_y[t])


def cav_pi_rule(m, t):
    if t != min(m.T) and t != max(m.T):
        return(m.cav_Pi[t] == m.cav_Pi[t-1] +
               3600/m.cav_m_0 * (m.cmp_m[t] - m.exp_m[t]))
    else:
        return(m.cav_Pi[t] == m.cav_Pi_0)


def exp_area_rule(m, t):
    return(m.exp_m[t] == (
        m.c0 + m.c * m.exp_P[t] + m.d * m.cav_Pi[t]) * m.cmp_y[t])


def cmp_p_range_max_rule(m, t):
    return(m.cmp_P[t] <= m.cmp_y[t] * m.cmp_P_max)


def cmp_p_range_min_rule(m, t):
    return(m.cmp_P[t] >= m.cmp_y[t] * m.cmp_P_min)


def exp_p_range_max_rule(m, t):
    return(m.exp_P[t] <= m.exp_y[t] * m.exp_P_max)


def exp_p_range_min_rule(m, t):
    return(m.exp_P[t] >= m.exp_y[t] * m.exp_P_min)


def cmp_exp_excl_rule(m, t):
    return(m.cmp_y[t] + m.exp_y[t] <= 1)


def exp_fuel_rule_1(m, t):
    return(m.exp_Q[t] == (
        m.exp_P[t] / m.exp_Eta_ex -
        m.exp_m[t] * m.exp_T_0 * m.exp_R * m.exp_ln))


def exp_fuel_rule_2(m, t):
    return(m.exp_Q[t] == (
        m.exp_m[t] * m.exp_cp * m.exp_Delta_T / m.exp_Eta_comb))
