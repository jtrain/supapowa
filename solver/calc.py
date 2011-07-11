from numpy import array
from numpy import dot
from math import cos, sin

def calc(nbus, bus_type, V, ang, Y, Pg, Qg, Pl, Ql, tol):
    """
    nbus - total number of buses.
    bus_type - load_bus(3), gen_bus(2), swing_bus(1)
    V - magnitude of bus voltage.
    ang - angle(rad) of bus votlage.
    Y - admittance matrix
    Pg - real power of generation.
    Qg - reactive power of generation.
    Pl - real power of load.
    Ql - reactive power of load.
    tol - a tolerance of computational error.
    """

    SWING_BUS, GEN_BUS, LOAD_BUS = 1, 2, 3

    V = V.flatten()
    # voltage in rectangular co-ordinates.
    V_rect = [V[i] * complex(cos(ang[i]), sin(ang[i])) for i in range(len(ang))]    
    V_rect = array(V_rect)

    # bus current injection.
    cur_inj = Y * V_rect

    # power output.
    S = V_rect * cur_inj.conj()
    P = S.real
    Q = S.imag
    delP = Pg.flatten() - Pl.flatten() - P
    delQ = Qg.flatten() - Ql.flatten() - Q

    # zero out mismatches on swing bus and generation bus.
    for i in range(nbus):
        if bus_type[i] == SWING_BUS:
            delP[i] = 0
            delQ[i] = 0
        elif bus_type[i] == GEN_BUS:
            delQ[i] = 0

    # total mismatch.
    mism = max(abs(delQ)) + max(abs(delP))
    if mism > tol:
        conv_flag = 1
    else:
        conv_flag = 0
    return delP, delQ, P, Q, conv_flag


    
