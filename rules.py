"""Objective and constraint rules for Compressed Air Energy Storages (CAES)."""
import pyomo.environ as po


# Add objective rules
def profit(m):
    """Objective function (costs-revenues)."""
    expr = (sum(m.mkt_C_el_cmp[t] * m.cmp_P[t] +
                m.mkt_C_fuel[t] * m.exp_Q[t] -
                m.mkt_C_el_exp[t] * m.exp_P[t]
            for t in m.T))
    return expr


# Add constraint rules
def cmp_p_range_min(m, t):
    """Minimum load range."""
    return(m.cmp_P[t] >= m.cmp_y[t] * m.cmp_P_min)


def cmp_p_range_max(m, t):
    """Maximum load range."""
    return(m.cmp_P[t] <= m.cmp_y[t] * m.cmp_P_max)


def cmp_area(m, t):
    """Relationship between power, mass flow and casern pressure."""
    return(m.cmp_m[t] == (
        m.a0 * m.cmp_y[t] + m.a * m.cmp_P[t] + m.b * m.cmp_z[t]
        + m.b * m.cas_Pi_min * m.cmp_y[t]))


def cmp_z1(m, t):
    """Linearization of variable product (cas_Pi_o * cmp_y)."""
    return(m.cmp_z[t] <= m.cas_Pi_o_max * m.cmp_y[t])


def cmp_z2(m, t):
    """Linearization of variable product (cas_Pi_o * cmp_y)."""
    return(m.cmp_z[t] <= m.cas_Pi_o[t])


def cmp_z3(m, t):
    """Linearization of variable product (cas_Pi_o * cmp_y)."""
    return(m.cmp_z[t] >= m.cas_Pi_o[t] - (1 - m.cmp_y[t]) * m.cas_Pi_o_max)


def cmp_z4(m, t):
    """Linearization of variable product (cas_Pi_o * cmp_y)."""
    return(m.cmp_z[t] >= 0)


def cas_pi(m, t):
    """casern balance for all timesteps but the first."""
    if t > 1:
        return(m.cas_Pi_o[t] == (1-m.eta)*m.cas_Pi_o[t-1] +
               3600/m.cas_m_0*(m.cmp_m[t] - m.exp_m[t]))
    else:
        return po.Constraint.Skip


def cas_pi_t0(m, t):
    """casern level in first and last timestep are set equal."""
    return(m.cas_Pi_o[min(m.T)] == m.cas_Pi_o_0)


def cas_pi_tmax(m, t):
    """casern level in first and last timestep are set equal."""
    return(m.cas_Pi_o[max(m.T)] == m.cas_Pi_o_0)


def exp_p_range_min(m, t):
    """Minimum load range."""
    return(m.exp_P[t] >= m.exp_y[t] * m.exp_P_min)


def exp_p_range_max(m, t):
    """Maximum load range."""
    return(m.exp_P[t] <= m.exp_y[t] * m.exp_P_max)


def exp_area1(m, t):
    """Relationship between power and mass flow."""
    return(m.exp_m[t] == m.exp_P[t] / m.c1)


def exp_area2(m, t):
    """Relationship between heat flow and mass flow."""
    return(m.exp_Q[t] == m.exp_m[t] * m.c2)


def cmp_exp_excl(m, t):
    """Exclusion of parallel operation of compression and expansion."""
    return(m.cmp_y[t] + m.exp_y[t] <= 1)
