"""Objective and constraint rules for Compressed Air Energy Storages (CAES)."""
import pyomo.environ as po



# -----------------------------------------------------------------------------
# ADD OBJECTIVE RULES
# -----------------------------------------------------------------------------
def profit(m):
    expr = (sum(m.mkt_C_el_cmp[t] * m.cmp_P[t] -
                m.mkt_C_el_exp[t] * m.exp_P[t] +
                m.mkt_C_fuel[t] * m.exp_Q[t]
            for t in m.T))
    return expr


# -----------------------------------------------------------------------------
# ADD CONSTRAINT RULES
# -----------------------------------------------------------------------------
def cmp_p_range_min(m, t):
    return(m.cmp_P[t] >= m.cmp_y[t] * m.cmp_P_min)


def cmp_p_range_max(m, t):
    return(m.cmp_P[t] <= m.cmp_y[t] * m.cmp_P_max)


def cmp_area(m, t):
    return(m.cmp_m[t] == (
        m.a0 * m.cmp_y[t] + m.a * m.cmp_P[t] + m.b * m.cmp_z[t]
        + m.b * m.cav_Pi_min * m.cmp_y[t]))


def cmp_z1(m, t):
    return(m.cmp_z[t] <= m.cav_Pi_o_max * m.cmp_y[t])


def cmp_z2(m, t):
    return(m.cmp_z[t] <= m.cav_Pi_o[t])


def cmp_z3(m, t):
    return(m.cmp_z[t] >= m.cav_Pi_o[t] - (1 - m.cmp_y[t]) * m.cav_Pi_o_max)


def cmp_z4(m, t):
    return(m.cmp_z[t] >= 0)


def cav_pi(m, t):
    if t > 1:
        return(m.cav_Pi_o[t] == (1-m.eta)*m.cav_Pi_o[t-1] +
               3600/m.cav_m_0*(m.cmp_m[t] - m.exp_m[t]))
    else:
        return po.Constraint.Skip


def cav_pi_t0(m, t):
    return(m.cav_Pi_o[min(m.T)] == m.cav_Pi_o_0)


def cav_pi_tmax(m, t):
    return(m.cav_Pi_o[max(m.T)] == m.cav_Pi_o_0)


def exp_p_range_min(m, t):
    return(m.exp_P[t] >= m.exp_y[t] * m.exp_P_min)


def exp_p_range_max(m, t):
    return(m.exp_P[t] <= m.exp_y[t] * m.exp_P_max)


def exp_area1(m, t):
    return(m.exp_m[t] == m.exp_P[t] / m.c1)


def exp_area2(m, t):
    return(m.exp_Q[t] == m.exp_m[t] * m.c2)


def cmp_exp_excl(m, t):
    return(m.cmp_y[t] + m.exp_y[t] <= 1)
