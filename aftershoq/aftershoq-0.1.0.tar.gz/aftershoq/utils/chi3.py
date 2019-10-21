"""
Module for calculating chi3 for FWM
"""

import numpy as np
from matplotlib import pyplot as pl
import scipy.constants as cn
from aftershoq.interface import Inegf

def THM(w, ni, Ei, zij, Gammaij):
    Nnu = len(ni)
    chi3 = 0.

    # sort according to Energy

    #index = np.argsort(Ei)[-1::-1]
    index = np.argsort(Ei)
    Ei = Ei[index]
    ni = ni[index]
    tmp1 = []
    tmp2 = []
    for i in range(Nnu):
        row = [Gammaij[index[i]][index[j]] for j in range(Nnu)]
        tmp1.append(row)
        row = [zij[index[i]][index[j]] for j in range(Nnu)]
        tmp2.append(row)
    Gammaij = np.array(tmp1)
    zij = np.array(tmp2)

    chi3 = cn.elementary_charge/cn.epsilon_0*ni[0]*zij[0,1]*zij[1,2]*zij[2,3]*zij[3,0]
    chi3 /= (w - Ei[1]+Ei[0]-1j*Gammaij[0,1])
    chi3 /= (2*w - Ei[2]+Ei[0]-1j*Gammaij[0,2])
    chi3 /= (3*w - Ei[3]+Ei[0]-1j*Gammaij[0,3])

    return chi3

def FWM1(wa,wb,ni,Ei,zij,Gammaij):

    chi3 = 0.

    return chi3

def chi3(wp, wa, wb, wc, ni, Ei, zij, Gammaij, termindex = None):
    """Calculates the general (24 Terms) 3rd order susceptibility
    according to Bloembergen et al Indian J. Pure Appl. Phys. 1978.

    Assumes symmtery of a heterostructure, chi3_zzzz is calculated.

    Parameters
    ----------
    wp : float
        Angluar frequency 1
    wa : float
        Angluar frequency 2
    wb : float
        Angluar frequency 3
    wc : float
        Angluar frequency 4
    ni : Array of float
        List of densities of each level.
    Ei : Array of float
        List of eigen-energy for each level.
    zij : type
        Matrix with broadening of each transition.
    Gammaij : array of array of float
        Matrix with broadening of each transition.

    Returns
    -------
    float
        The thrird order non-linear susceptibility.

    """

    printterms = False

    if termindex is None:
        Nnu = len(ni)
        indices = []
        start = [0,0,0,0]
        end = [Nnu,Nnu,Nnu,Nnu]
    else:
        printterms = True
        start = termindex[0:4]
        end = np.array(termindex[0:4])+1

    chi3_sum = 0.
    maxchi3 = 0.


    Om1 = wa + wb
    Om2 = wa - wc
    Om3 = wb - wc

    Ek = Ei[start[1]:end[1]]

    for g in range(start[0],end[0]):
        Eg = Ei[g]
        ng = ni[g]
        zgk = zij[g,start[1]:end[1]]
        Gkg = Gammaij[start[1]:end[1],g]
        wkg = Ek - Eg - 1j*Gkg/2.
        for j in range(start[3],end[3]):
            zjg = zij[j,g]
            Ej = Ei[j]
            Gjg = Gammaij[j,g]
            wjg = Ej - Eg - 1j*Gjg/2.
            Gkj = Gammaij[start[1]:end[1],j]
            wkj = Ek - Ej - 1j*Gkj/2.
            for t in range(start[2],end[2]):
                ztj = zij[t,j]
                Et = Ei[t]
                Gtj = Gammaij[t,j]
                Gtg = Gammaij[t,g]
                wtj = Et - Ej - 1j*Gtj/2.
                wtg = Et - Eg - 1j*Gtg/2.
                K = 1j*(Gtj - Gtg - Gjg)
                '''
                for k in range(Nnu):
                    zkt = zij[k,t]
                    zgk = zij[g,k]
                    Ek = Ei[k]
                    Gkj = Gammaij[k,j]
                    Gtk = Gammaij[k,t]
                    Gkg = Gammaij[k,g]
                    wkj = Ek - Ej - 1j*Gkj/2.
                    wtk = Et - Ek - 1j*Gtk/2.
                    wkg = Ek - Eg - 1j*Gkg/2.

                    chi3 = 0.
                '''
                zkt = zij[start[1]:end[1],t]
                Gtk = Gammaij[start[1]:end[1],t]
                wtk = Et - Ek - 1j*Gtk/2.


                chi3 = 0.
                maxterm = 0.

                if printterms:
                    print(f'wtg={wtg}, wkg={wkg}, wjg={wjg}')
                    print(f'Eg={Ei[g]}, Ek={Ek}, Et={Ei[t]}, Ej={Ei[j]}')

                # ===== Term 1-2 ======
                K1 = K + 1j*(Gkj - Gkg - Gjg)*(wtg-Om3)/(wkg-Om2)/(wtj-wp)
                K1 /= (wtj-wp)
                term = 1./((wtg - (wb-wc))*(wkg+wc) )
                term *= 1./(wjg - wp)+(1+K1)/(np.conj(wjg)+wa)

                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    termindex = 1


                chi3+=term

                # ===== Term 3-4 ======
                K1 = K + 1j*(Gkj - Gkg - Gjg)*(wtg-Om3)/(wkg-Om1)
                K1 /= (wtj-wp)
                term = 1./((wtg - (wb-wc))*(wkg-wb) )
                term *= 1./(wjg - wp)+(1+K1)/(np.conj(wjg)+wa)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    K1 = np.argmax(np.abs(term))
                    termindex = 3

                chi3+=term

                # ===== Term 5-6 ======

                K1 = K +  1j*(Gkj - Gkg - Gjg)*(wtg-Om1)/(wkg-Om3)
                K1 /= (wtj-wp)
                term = 1./((wtg - (wa-wc))*(wkg+wc) )
                term *= 1./(wjg - wp)+(1+K1)/(np.conj(wjg)+wb)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    termindex = 5

                chi3+=term

                # ===== Term 7-8 ======

                K1 = K +  1j*(Gkj - Gkg - Gjg)*(wtg-Om2)/(wkg-Om1)
                K1 /= (wtj-wp)
                term = 1./((wtg - (wa-wc))*(wkg-wa) )
                term *= 1./(wjg - wp)+(1+K1)/(np.conj(wjg)+wb)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    termindex = 7

                chi3+=term

                # ===== Term 9-10 ======

                K1 = K +  1j*(Gkj - Gkg - Gjg)*(wtg-Om1)/(wkg-Om3)
                K1 /= (wtj-wp)
                term = 1./((wtg - (wa+wb))*(wkg-wb) )
                term *= 1./(wjg - wp)+(1+K1)/(np.conj(wjg)-wc)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    termindex = 9

                chi3+=term

                # ===== Term 11-12 ======

                K1 = K +  1j*(Gkj - Gkg - Gjg)*(wtg-Om1)/(wkg-Om2)
                K1 /= (wtj-wp)
                term = 1./((wtg - (wa+wb))*(wkg-wa) )
                term *= 1./(wjg - wp)+(1+K1)/(np.conj(wjg)-wc)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    termindex = 11

                chi3+=term

                # ===== Term 13-14 ======

                K2 = K + 1j*(Gkj - Gkg - Gjg)*(np.conj(wtg)+Om3)/(wkj-Om2)
                K2 /= (np.conj(wtk)+wp)
                term = 1./((np.conj(wtg) + wb - wc)*(np.conj(wjg)-wc) )
                term *= 1./(np.conj(wkg) + wp)+(1+K2)/(wkg-wa)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    termindex = 13

                chi3+=term

                # ===== Term 15-16 ======

                K2 = K + 1j*(Gkj - Gkg - Gjg)*(np.conj(wtg)+Om3)/(wkj-Om1)
                K2 /= (np.conj(wtk)+wp)
                term = 1./((np.conj(wtg) + wb - wc)*(np.conj(wjg)+wb) )
                term *= 1./(np.conj(wkg) + wp)+(1+K2)/(wkg-wa)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    termindex = 15

                chi3+=term

                # ===== Term 17-18 ======

                K2 = K + 1j*(Gkj - Gkg - Gjg)*(np.conj(wtg)+Om2)/(wkj-Om3)
                K2 /= (np.conj(wtk)+wp)
                term = 1./((np.conj(wtg) + wa - wc)*(np.conj(wjg)-wc) )
                term *= 1./(np.conj(wkg) + wp)+(1+K2)/(wkg-wb)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    termindex = 17

                chi3+=term

                # ===== Term 19-20 ======

                K2 = K + 1j*(Gkj - Gkg - Gjg)*(np.conj(wtg)+Om2)/(wkj-Om1)
                K2 /= (np.conj(wtk)+wp)
                term = 1./((np.conj(wtg) + wa - wc)*(np.conj(wjg)+wa) )
                term *= 1./(np.conj(wkg) + wp)+(1+K2)/(wkg-wb)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    termindex = 19

                chi3+=term

                # ===== Term 21-22 ======

                K2 = K + 1j*(Gkj - Gkg - Gjg)*(np.conj(wtg)+Om1)/(wkj-Om3)
                K2 /= (np.conj(wtk)+wp)
                term = 1./((np.conj(wtg) + wa + wb)*(np.conj(wjg)+wb) )
                term *= 1./(np.conj(wkg) + wp)+(1+K2)/(wkg+wc)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    termindex = 21

                chi3+=term

                # ===== Term 21-22 ======

                K2 = K + 1j*(Gkj - Gkg - Gjg)*(np.conj(wtg)+Om1)/(wkj-Om2)
                K2 /= (np.conj(wtk)+wp)
                term = 1./((np.conj(wtg) + wa + wb)*(np.conj(wjg)+wa) )
                term *= 1./(np.conj(wkg) + wp)+(1+K2)/(wkg+wc)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    termindex = 23

                chi3+=term

                # === Common factors ===

                chi3 = chi3*zgk*zkt*ztj*zjg*ng

                if np.max(np.abs(chi3)) > maxchi3:
                    maxchi3 = np.max(np.abs(chi3))
                    if termindex is None:
                        k = np.argmax(np.abs(chi3))
                    else:
                        k = start[1]
                    indices = [g,k,t,j,termindex]

                chi3_sum += np.sum(chi3)

    return chi3_sum*cn.elementary_charge/6./cn.epsilon_0, indices, maxchi3


def chi3_ordered_wrong(wp, wa, wb, wc, ni, Ei, zij, Gammaij):
    """Calculates the general (24 Terms) 3rd order susceptibility
    according to Bloembergen et al Indian J. Pure Appl. Phys. 1978.

    Assumes symmtery of a heterostructure, chi3_zzzz is calculated.

    Parameters
    ----------
    wp : float
        Angluar frequency 1
    wa : float
        Angluar frequency 2
    wb : float
        Angluar frequency 3
    wc : float
        Angluar frequency 4
    ni : Array of float
        List of densities of each level.
    Ei : Array of float
        List of eigen-energy for each level.
    zij : type
        Matrix with broadening of each transition.
    Gammaij : array of array of float
        Matrix with broadening of each transition.

    Returns
    -------
    float
        The thrird order non-linear susceptibility.

    """

    Nnu = len(ni)
    chi3_sum = 0.
    maxterm = 0.

    # sort according to Energy

    #index = np.argsort(Ei)[-1::-1]
    index = np.argsort(Ei)
    Ei = Ei[index]
    ni = ni[index]
    tmp1 = []
    tmp2 = []
    for i in range(Nnu):
        row = [Gammaij[index[i]][index[j]] for j in range(Nnu)]
        tmp1.append(row)
        row = [zij[index[i]][index[j]] for j in range(Nnu)]
        tmp2.append(row)
    Gammaij = np.array(tmp1)
    zij = np.array(tmp2)

    indices = []
    Om1 = wa + wb
    Om2 = wa - wc
    Om3 = wb - wc

    for j in range(3,Nnu):
        Ej = Ei[j]
        nj = ni[j]
        for t in range(2,j):
            ztj = zij[j,t]
            Et = Ei[t]
            Gtj = Gammaij[j,t]
            wtj = Et - Ej - 1j*Gtj
            for k in range(1,t):
                zkj = zij[k,j]
                zkt = zij[k,t]
                Ek = Ei[k]
                Gkj = Gammaij[k,j]
                Gtk = Gammaij[t,k]
                wkj = Ek - Ej - 1j*Gkj
                wtk = Et - Ek - 1j*Gtk

                '''
                for g in range(0,k):
                    zkt = zij[k,t]
                    zgk = zij[g,k]
                    Ek = Ei[k]
                    Gkj = Gammaij[k,j]
                    Gtk = Gammaij[k,t]
                    Gkg = Gammaij[k,g]
                    wkj = Ek - Ej - 1j*Gkj
                    wtk = Et - Ek - 1j*Gtk
                    wkg = Ek - Eg - 1j*Gkg

                    chi3 = 0.
                '''
                zgk = zij[0:k,k]
                ztg = zij[t,0:k]
                zjg = zij[j,0:k]
                Eg = Ei[0:k]
                ng = ni[0:k]
                Gkg = Gammaij[k,0:k]
                Gtg = Gammaij[t,0:k]
                Gjg = Gammaij[j,0:k]
                wkg = Ek - Eg - 1j*Gkg
                wjg = Ej - Eg - 1j*Gjg
                wtg = Et - Eg - 1j*Gtg
                K = 1j*(Gtj - Gtg - Gjg)
                chi3 = 0.

                # ===== Term 1-2 ======
                K1 = K + 1j*(Gkj - Gkg - Gjg)*(wtg-Om3)/(wkg-Om2)/(wtj-wp)
                K1 /= (wtj-wp)
                term = 1./((wtg - (wb-wc))*(wkg+wc) )
                term *= 1./(wjg - wp)+(1+K1)/(np.conj(wjg)+wa)

                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    g = np.argmax(np.abs(term))
                    indices = [g,k,t,j,1]


                chi3+=term

                # ===== Term 3-4 ======
                K1 = K + 1j*(Gkj - Gkg - Gjg)*(wtg-Om3)/(wkg-Om1)
                K1 /= (wtj-wp)
                term = 1./((wtg - (wb-wc))*(wkg-wb) )
                term *= 1./(wjg - wp)+(1+K1)/(np.conj(wjg)+wa)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    g = np.argmax(np.abs(term))
                    indices = [g,k,t,j,3]

                chi3+=term

                # ===== Term 5-6 ======

                K1 = K +  1j*(Gkj - Gkg - Gjg)*(wtg-Om1)/(wkg-Om3)
                K1 /= (wtj-wp)
                term = 1./((wtg - (wa-wc))*(wkg+wc) )
                term *= 1./(wjg - wp)+(1+K1)/(np.conj(wjg)+wb)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    g = np.argmax(np.abs(term))
                    indices = [g,k,t,j,5]

                chi3+=term

                # ===== Term 7-8 ======

                K1 = K +  1j*(Gkj - Gkg - Gjg)*(wtg-Om2)/(wkg-Om1)
                K1 /= (wtj-wp)
                term = 1./((wtg - (wa-wc))*(wkg-wa) )
                term *= 1./(wjg - wp)+(1+K1)/(np.conj(wjg)+wb)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    g = np.argmax(np.abs(term))
                    indices = [g,k,t,j,7]

                chi3+=term

                # ===== Term 9-10 ======

                K1 = K +  1j*(Gkj - Gkg - Gjg)*(wtg-Om1)/(wkg-Om3)
                K1 /= (wtj-wp)
                term = 1./((wtg - (wa+wb))*(wkg-wb) )
                term *= 1./(wjg - wp)+(1+K1)/(np.conj(wjg)-wc)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    g = np.argmax(np.abs(term))
                    indices = [g,k,t,j,9]

                chi3+=term

                # ===== Term 11-12 ======

                K1 = K +  1j*(Gkj - Gkg - Gjg)*(wtg-Om1)/(wkg-Om2)
                K1 /= (wtj-wp)
                term = 1./((wtg - (wa+wb))*(wkg-wa) )
                term *= 1./(wjg - wp)+(1+K1)/(np.conj(wjg)-wc)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    g = np.argmax(np.abs(term))
                    indices = [g,k,t,j,11]

                chi3+=term

                # ===== Term 13-14 ======

                K2 = K + 1j*(Gkj - Gkg - Gjg)*(np.conj(wtg)+Om3)/(wkj-Om2)
                K2 /= (np.conj(wtk)+wp)
                term = 1./((np.conj(wtg) + wb - wc)*(np.conj(wjg)-wc) )
                term *= 1./(np.conj(wkg) + wp)+(1+K2)/(wkg-wa)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    g = np.argmax(np.abs(term))
                    indices = [g,k,t,j,13]

                chi3+=term

                # ===== Term 15-16 ======

                K2 = K + 1j*(Gkj - Gkg - Gjg)*(np.conj(wtg)+Om3)/(wkj-Om1)
                K2 /= (np.conj(wtk)+wp)
                term = 1./((np.conj(wtg) + wb - wc)*(np.conj(wjg)+wb) )
                term *= 1./(np.conj(wkg) + wp)+(1+K2)/(wkg-wa)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    g = np.argmax(np.abs(term))
                    indices = [g,k,t,j,15]

                chi3+=term

                # ===== Term 17-18 ======

                K2 = K + 1j*(Gkj - Gkg - Gjg)*(np.conj(wtg)+Om2)/(wkj-Om3)
                K2 /= (np.conj(wtk)+wp)
                term = 1./((np.conj(wtg) + wa - wc)*(np.conj(wjg)-wc) )
                term *= 1./(np.conj(wkg) + wp)+(1+K2)/(wkg-wb)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    g = np.argmax(np.abs(term))
                    indices = [g,k,t,j,17]

                chi3+=term

                # ===== Term 19-20 ======

                K2 = K + 1j*(Gkj - Gkg - Gjg)*(np.conj(wtg)+Om2)/(wkj-Om1)
                K2 /= (np.conj(wtk)+wp)
                term = 1./((np.conj(wtg) + wa - wc)*(np.conj(wjg)+wa) )
                term *= 1./(np.conj(wkg) + wp)+(1+K2)/(wkg-wb)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    g = np.argmax(np.abs(term))
                    indices = [g,k,t,j,19]

                chi3+=term

                # ===== Term 21-22 ======

                K2 = K + 1j*(Gkj - Gkg - Gjg)*(np.conj(wtg)+Om1)/(wkj-Om3)
                K2 /= (np.conj(wtk)+wp)
                term = 1./((np.conj(wtg) + wa + wb)*(np.conj(wjg)+wb) )
                term *= 1./(np.conj(wkg) + wp)+(1+K2)/(wkg+wc)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    g = np.argmax(np.abs(term))
                    indices = [g,k,t,j,21]

                chi3+=term

                # ===== Term 21-22 ======

                K2 = K + 1j*(Gkj - Gkg - Gjg)*(np.conj(wtg)+Om1)/(wkj-Om2)
                K2 /= (np.conj(wtk)+wp)
                term = 1./((np.conj(wtg) + wa + wb)*(np.conj(wjg)+wa) )
                term *= 1./(np.conj(wkg) + wp)+(1+K2)/(wkg+wc)
                if np.max(np.abs(term)) > maxterm:
                    maxterm = np.max(np.abs(term))
                    g = np.argmax(np.abs(term))
                    indices = [g,k,t,j,23]

                chi3+=term

                # === Common factors ===

                chi3 = chi3*zgk*zkt*ztj*zjg*ng

                chi3_sum += np.sum(chi3)

    return chi3_sum/6./cn.epsilon_0*cn.elementary_charge, indices, maxterm
