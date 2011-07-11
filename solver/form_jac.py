from math import sin, cos
from numpy import array
from numpy import ones
from numpy import concatenate as cat

from scipy.sparse import lil_matrix as sparse
from ybus import make_sparse

def form_jac(V, ang, Y, ang_red, volt_red):
    """
    V - magnitude of bus voltage.
    ang - angle(rad) of bus voltage.
    Y - admittance matrix.
    ang_red - vector to eliminate swing bus entries.
    volt_red - vector to eliminate generator bus entries.
    """

    V = array(V)
    k, dum = Y.shape
    cosang = array([cos(angl) for angl in array(ang)])
    sinang = array([sin(angl) for angl in array(ang)])
    # voltage peterbation rectangular co-ordinates.
    L = len(cosang)
    V_pert = array([complex(cosang[i], sinang[i]) for i in range(L)])
    # Voltage rectangular co-ordinates. 
    V_rect = array([V[i] * V_pert[i] for i in range(L)])
    # angle and voltage perturbation rectangular coordinates.
    rect_angs = array([complex(sinang[i], -cosang[i]) for i in range(L)])
    ang_pert = array([-V[i] * rect_angs[i] for i in range(L)])

    V_1_bar = Y * V_rect
    V_1 = V_1_bar.conj()
    V_1.resize((len(V_1), 1))

    # sparse matrix formulation of V_2.
    indexes = range(k)
    temp = make_sparse(indexes, indexes, V_rect, k, k)
    V_2 = temp * Y.conj()

    # sparse matrix formulation of X_1.
    X_1 = make_sparse(indexes, indexes, V_1 * ang_pert, k, k)
    X_1 = X_1 + V_2 * make_sparse(indexes, indexes, ang_pert.conj(), k, k)

    # sparse matrix formulation of XX_1.
    lang = len(ang_red)
    ilang = range(lang)
    x_red = make_sparse(roundoff(ang_red), ilang, ones((lang, 1)), k, lang)
    XX_1 = X_1 * x_red

    # sparse matrix formulation of X_2.
    X_2 = make_sparse(indexes, indexes, V_1 * V_pert, k, k)
    X_2 = X_2 + V_2 * make_sparse(indexes, indexes, V_pert.conj(), k, k)

    # sparse matrix formulation of XX_2. 
    lvolt = len(volt_red)
    ilvolt = range(lvolt)
    x_volt = make_sparse(roundoff(volt_red), ilvolt, ones((lvolt, 1)), k, lvolt)
    XX_2 = X_2 * x_volt

    # sparse matrix formulation of J.
    temp = make_sparse(ilang, roundoff(ang_red), ones((lang, 1)), lang, k)
    J11 = temp * XX_1.real
    J12 = temp * XX_2.real
    temp = make_sparse(ilvolt, roundoff(volt_red), ones((lvolt, 1)), lvolt, k)
    J21 = temp * XX_1.imag
    J22 = temp * XX_2.imag
   
    row1 = cat((J11.toarray(), J12.toarray()), axis=1)
    row2 = cat((J21.toarray(), J22.toarray()), axis=1)
    return sparse(cat((row1, row2), axis=0))

def roundoff(lst):
    return [round(val) for val in lst]
