# -*- coding: utf-8 -*-
import dvtDecimal

def isInteger(n, tolerance=1e-2):
    return abs(n - round(n)) <= tolerance


# lqp : liste des quotients partiels
# càd les termes du dvt en fractions continues
def ratApp(lqp):
        if len(lqp) == 1:
            return dvtDecimal.dvtDecimal(lqp[0], 1)
        else:
            p = [lqp[0], lqp[1] * lqp[0] + 1]
            q = [1, lqp[1]]
            m = 2
            while m < len(lqp):
                p += [lqp[m] * p[m - 1] + p[m - 2]]
                q += [lqp[m] * q[m - 1] + q[m - 2]]
                m += 1
            return [dvtDecimal.dvtDecimal(r, s) for r, s in zip(p, q)]


# fraction continue de racine (d'un entier)
# à améliorer en sachant qu'arriver à 2*a1 signifie
# avoir trouver toutes la partie périodique
# à utiliser genre :
# contFractionQ(math.sqrt(2))
# contFractionQ((1+math.sqrt(5))/2)
def contFractionQ(racine):
    r = racine
    e = int(r)
    lFC = [e]
    lSous = []
    # 4 chiffres après la virgule
    s = round(r - e, 4)
    while s not in lSous:
        lSous.append(s)
        r = 1 / (r - e)
        e = int(r)
        lFC.append(e)
        s = round(r - e, 4)
    debut = lSous.index(s) + 1
    return [*lFC[:debut], lFC[debut:]]


# prend une liste de deux éléments
# résultat de egyptG2
# et l'écrit en Somme de fraction TeX
def egToTeX(liste):
    ll = len(liste)
    if ll == 0:
        return
    else:
        s = ''
        for i in range(ll):
            s += "{1\\over" + str(liste[i]) + "}"
            if i != ll - 1:
                s += "+"
        return s


# d'une fraction continue finie à l'écriture TeX
def cfToTeX(liste):
    ll = len(liste)
    dps = "\\displaystyle"
    og = "{"
    fg = "}"
    textF = "\\strut1\\over"
    if ll == 0:
        return
    else:
        s = str(liste[0]) + "+" + dps
        for i in range(1, ll - 1):
            s += og + textF + dps + str(liste[i]) + "+"
        s += og + textF + str(liste[i + 1]) + fg*(ll - 1)
    return s

# liste est de la forme [1, 2, [3, 4]]
# index est l'indice de fin, après: ...
def cfQToTex(liste, index):
    ll = len(liste)
    dps = "\\displaystyle"
    og = "{"
    fg = "}"
    textF = "\\strut1\\over"
    if ll == 0:
        return
    else:
        ppartie = []
        i = 0
        while type(liste[i]) == int:
            ppartie += [liste[i]]
            i += 1
        periode = liste[i]
        lperiode = len(periode)
        lppartie = len(ppartie)
        # avant la période
        s = str(liste[0]) + "+" + dps
        i = 1
        while i < index:
            if i < lppartie:
                element = str(liste[i])
            else:
                element = str(periode[(i - lppartie) % lperiode])
            s += og + textF + dps + element + "+"
            i += 1
        s += og + textF + dps + "\\dots" + fg*(index)
        return s


