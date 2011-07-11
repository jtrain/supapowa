import time
from math import pi, sin, cos
from numpy import ones, ix_, zeros
from numpy import array, matrix, asarray
from numpy import concatenate as cat
from numpy import hstack, reshape
from numpy.linalg import solve
from scipy.linsolve import spsolve
from scipy.sparse import lil_matrix as sparse

from ybus import ybus
from ybus import make_sparse
from calc import calc
from form_jac import form_jac

def loadflow(bus, line, tol, iter_max, vmin, vmax, acc, display, flag=1):
    """
    bus - bus data.
    line - line data.
    tol - tolerance for convergence.
    iter_max - maximum number of iterations.
    vmin - voltage minimum limit.
    vmax - voltage maximum limit.
    acc - acceleration factor.
    display - 'y' generate load-flow study report.
                else, no load-flow study report.
    flag - 1, form new jacobian every iteration.
           2, form new jacobian every other iteration.
    """
    tt = time.time()
    LOAD_BUS, GEN_BUS, SWING_BUS = 3,2,1
    if flag < 1 or flag > 2:
        raise NotImplementedError('LOADFLOW: flag not recognised')

    nline = len(line[:,0])
    nbus = len(bus[:,0])
    # set maximum and minimum voltage.
    volt_min = vmin * ones((1, nbus))
    volt_max = vmax * ones((1, nbus))
    # build admittance matrix y
    Y, nSW, nPV, nPQ, SB, bus_int = ybus(bus, line, 2)
    
    # process bus data.
    bus_no = array(bus[:,0])
    V = array(bus[:,1])
    ang = array(bus[:,2]) * pi / 180
    Pg = array(bus[:,3])
    Qg = array(bus[:,4])
    Pl = array(bus[:,5])
    Ql = array(bus[:,6])
    Gb = array(bus[:,7])
    Bb = array(bus[:,8])
    bus_type = array(bus[:,9])

    # set up index for jacobian calculation.

    # form PQV_no and PQ_no.
    PQVptr = 1
    PQptr = 1

    PQV_no = []
    PQ_no = []
    try:
        for i in range(nbus):
            if bus_type[i] == LOAD_BUS:
                PQV_no.append(i)
                PQ_no.append(i)
            elif bus_type[i] == GEN_BUS:
                PQV_no.append(i)
    except ValueError:
        print bus_type
        raise

    # construct angle reduction matrix.
    il = len(PQV_no)
    ii = range(il)
    ang_red = make_sparse(ii, PQV_no, ones((il, 1)), il, nbus)

    # construct voltage reduction matrix.
    il = len(PQ_no)
    ii = range(il)
    volt_red = make_sparse(ii, PQ_no, ones((il, 1)), il, nbus)

    # iteration counter.
    iter = 0
    delP, delQ, P, Q, conv_flag = calc(nbus, bus_type, V, ang, Y, Pg, Qg, Pl,
            Ql, tol)

    st = time.time()
    # start iteration process.
    while conv_flag == 1 and iter < iter_max:
        iter += 1
        if flag == 2:
            if iter == 2 * iter / 2 + 1:
                jac = form_jac(V, ang, Y, PQV_no, PQ_no)
        else:
            jac = form_jac(V, ang, Y, PQV_no, PQ_no)
        
        # reduced mismatch real and reactive power vectors.
        red_delP = ang_red * delP
        red_delQ = volt_red * delQ

        # solve for voltage magnitude and phase angle increments.
        # form the denominator. 
        denom = cat((red_delP, red_delQ), axis=1)
        # computes the solution to A * X = B
        temp = sparse(spsolve(jac, denom))

        # expand solution vectors to all buses.
        delAng = temp[0,:len(PQV_no)] * ang_red
        delV = temp[0,len(PQV_no):len(PQV_no)+len(PQ_no)] * volt_red

        # update voltage magnitude and phase angle.
        if delV.size == 0:
            delV = zeros(V.shape)

        V = sparse(V) + acc * delV.transpose()
        V = sparse([max(V[i,0][0], volt_min[0][i]) for i in range(V.shape[0])]).transpose()
        V = sparse([min(V[i,0][0], volt_max[0][i]) for i in range(V.shape[0])]).transpose()
        V = V.toarray()

        ang = sparse(ang) + acc * delAng.transpose()
        ang = ang.real.toarray()

        delP, delQ, P, Q, conv_flag = calc(nbus, bus_type, V, ang, Y, Pg, Qg, Pl, Ql, tol)
    ste = time.time()

    for i in range(nbus):
        if bus_type[i] == GEN_BUS:
            Pg[i] = P[i] + Pl[i]
            Qg[i] = Q[i] + Ql[i]
        elif bus_type[i] == LOAD_BUS:
            Pl[i] = Pg[i] - P[i]
            Ql[i] = Qg[i] - Q[i]

    Pg[SB] = P[SB] + Pl[SB]
    Qg[SB] = Q[SB] + Ql[SB]
    # solution voltage.
    VV = V * rect(ang)

    # calculate the line flows and power losses.
    tap_ratio = []
    for i in range(nline):
        tap_ratio.append(line[i,5])
        if tap_ratio[i] == 0:
            # this line has no transformer.
            tap_ratio[i] = 1

    phase_shift = array(line[:,6]) * pi / 180
    tps = array(tap_ratio, ndmin=2).transpose() * rect(phase_shift)

    # convert line[:,0] from a matrix column to an integer array.
    from_bus = type_array(line[:,0], int)
    # get the indexes specified in from bus from bus_int and convert to an
    #  array of integers.
    from_int = type_array(bus_int[ix_(from_bus)], int)
    to_bus = type_array(line[:,1], int)
    to_int = type_array(bus_int[ix_(to_bus)], int)
    r = line[:,2]
    rx = line[:,3]
    chrg = line[:,4]
    z = matrix([complex(r[i],rx[i]) for i in range(nline)])
    y = array(ones((nline,1))/z.transpose())

    MW_s = VV[ix_(from_int)] * conj((VV[ix_(from_int)] - 
        tps * VV[ix_(to_int)]) * y + VV[ix_(from_int)] * (jay() * 
        0.5 * asarray(chrg))) / (tps * tps.conj())
    # active power sent out by from_bus to to_bus.
    P_s = MW_s.real
    # reactive power sent out by from_bus to to_bus.
    Q_s = MW_s.imag

    MW_r = VV[ix_(to_int)] * conj((VV[ix_(to_int)] - 
        VV[ix_(from_int)] / tps) * y + 
        VV[ix_(to_int)] * (jay() * 0.5 * asarray(chrg)))
    # active power received by to_bus from from_bus.
    P_r = MW_r.real
    # reactive power received by to_bus from from_bus.
    Q_r = MW_r.imag

    line_flow = zeros((nline * 2,5))
    for i in range(nline):
        line_flow[2 * i: 2 * i + 2, :] = array([[i, from_bus[i], to_bus[i],
            P_s[i], Q_s[i]], [i, to_bus[i], from_bus[i], P_r[i], Q_r[i]]])
    P_loss = P_s.sum() + P_r.sum()
    Q_loss = Q_s.sum() + Q_r.sum()
    bus_sol = hstack([bus_no, V.reshape(nbus, 1), ang * 180 / pi, 
        Pg, Qg, Pl, Ql, Gb, Bb, bus_type]).real

    if display == 'y':
        import datetime
        print '                             LOAD-FLOW STUDY'
        print '                    REPORT OF POWER FLOW CALCULATIONS '
        print ' '
        print datetime.datetime.now().strftime('%d-%b-%y')
        print 'SWING BUS                  : BUS %g ' % SB
        print 'NUMBER OF ITERATIONS       : %g '% iter
        print 'SOLUTION TIME              : %g sec.'% (ste - st)
        print 'TOTAL TIME                 : %g sec.'% (time.time() - tt)
        print 'TOTAL REAL POWER LOSSES    : %g.'%P_loss
        print 'TOTAL REACTIVE POWER LOSSES: %g.\n'%Q_loss
        if conv_flag == 0:
            print '                                      GENERATION             LOAD'
            print '       BUS     VOLTS     ANGLE      REAL  REACTIVE      REAL  REACTIVE '
            print bus_sol[:,0:6]
            
            print '                      LINE FLOWS                     '
            print '      LINE  FROM BUS    TO BUS      REAL  REACTIVE   '
            print line_flow
    if iter > iter_max:
        print 'Note: Solution did not converge in %g iterations' % iter_max

    return bus_sol, line_flow
        


def jay():
    return complex(0,1)
def conj(vals):
    return vals.conj()

def type_array(vector, type):
    return asarray(vector).flatten().astype(type)
        
def rect(lst):
    try:
        tmp = array([complex(cos(item), sin(item)) for item in lst.toarray().real])
        return reshape(tmp, lst.toarray().shape)
    except AttributeError:
        tmp = array([complex(cos(item), sin(item)) for item in lst])
        return reshape(tmp, lst.shape)






