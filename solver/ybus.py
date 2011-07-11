import scipy
from scipy.sparse import lil_matrix as sparse
from math import pi
from math import cos, sin
from numpy import zeros
from numpy import matrix
from numpy import array
from numpy import ones

__all__ = ['ybus']

def ybus(bus, line, nargout=0):
    """
    output:
        Y - admittance matrix
        nSW - number of swing buses
        nPV - number of generator buses
        nPQ - number of load buses
        SB - bus number of swing bus
    """
    
    SWING_BUS, GEN_BUS, LOAD_BUS = 1, 2, 3
    j = complex(0,1)

    nline = len(line[:,0])
    nbus = len(bus[:,0])

    # a sparse matrix of 0's.
    Y = sparse((nbus,nbus), dtype=scipy.complex128)

    busmax = max(bus[:,0]) + 1
    bus_int = zeros((busmax, 1))
    ibus = matrix(range(nbus)).transpose()
    for i in range(nbus):
        bus_int[int(bus[i,0])] = i

    # process line data and build admittance matrix Y
    r = line[:,2]
    rx = line[:,3]
    chrg = line[:,4]
    z = matrix([complex(r[i],rx[i]) for i in range(nline)])
    y = array(ones((nline,1))/z.transpose()).flatten()

    for i in range(nline):
        from_bus = line[i,0]
        from_int = bus_int[int(from_bus)]
        to_bus = line[i,1]
        to_int = bus_int[int(to_bus)]
        tap_ratio = line[i,5]
        if tap_ratio == 0:
            # this line has no tx.
            tap_ratio = 1
        phase_shift = line[i,6]
        tps = tap_ratio * exp(j * phase_shift * pi / 180)

        j1 = array(zeros((4,1)))
        j2 = array(zeros((4,1)))
        w = array([[complex(1,2)], [0], [0], [0]])
        j1[0,0] = from_int
        j2[0,0] = to_int
        w[0,0] = -1 * y[i] / tps.conjugate()
        j1[1,0] = to_int
        j2[1,0] = from_int
        w[1,0] = -1 * y[i] / tps
        j1[2,0] = from_int
        j2[2,0] = from_int
        w[2,0] = complex(y[i], chrg[i] / 2.0) / (tps * tps.conjugate())
        j1[3,0] = to_int
        j2[3,0] = to_int
        w[3,0] = complex(y[i], chrg[i] / 2.0)
        Y = Y + make_sparse(j1, j2, w, nbus, nbus)

    # bus conductance.
    Gb = bus[:,7]
    # bus susceptance.
    Bb = bus[:,8]

    comp_bus = array([complex(Gb[i], Bb[i]) for i in range(nbus)])
    Y = Y + make_sparse(ibus, ibus, comp_bus, nbus, nbus)

    if nargout > 1:
        nSW = 0
        nPV = 0
        nPQ = 0
        for i in range(nbus):
            bus_type = bus[i,9]
            if bus_type == SWING_BUS:
                SB = int(bus_int[int(bus[i,0])])
                nSW = nSW + 1
            elif bus_type == GEN_BUS:
                nPV += 1
            else:
                nPQ += 1
        return Y, nSW, nPV, nPQ, SB, bus_int
    else:
        return Y, bus_int

def make_sparse(a, b, w, n, m):
    s = sparse((n,m), dtype=scipy.complex128)
    for i, value in enumerate(a):
        try:
            s[int(a[i]), int(b[i])] = w[i][0]
        except: 
            s[int(a[i]), int(b[i])] = w[i]

    return s

def exp(exponent):
    realp = exponent.real
    imagp = exponent.imag
    return complex(cos(realp), sin(imagp))
