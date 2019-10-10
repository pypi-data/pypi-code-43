# -*- coding: utf-8 -*-
import os
import sys
from .dvtDecimalTools import *


class dvtDecimal:
    """classe d'écriture d'un nombre en fraction
    à numérateur et dénominateur entiers.
    Le principe est simple :
    - la fraction est simplifiée (pgcd)
    - on fait en sorte que le dénominateur et 10
    soient premiers entre eux
    - on isole notre partie entière, notre partie
    irégulière et notre fraction avec den. premier
    avec 10
    - on calcule par div. successives sur cette
    dernière fraction notre partie qui se répète
    """

    def __init__(self, *args):
        # si deux arguments : num et den
        if len(args) == 2:
            self._initFraction(args[0], args[1])
        # si un argument avec . : nombre décimal
        elif type(args[0]) == float:
            self._initFloat(args[0])
        # si un argmuent sans . : une période
        elif type(args[0]) == int:
            self._initFraction(args[0], 1)
        # si un argmuent sans . : une période
        elif type(args[0]) == str:
            self._initStr(args[0])
        else:
            print("Can't understand your input!")
            quit()
    
    def _initFraction(self, p, q):
        """initialisation des objets de la classe"""
        # determination du signe
        if p * q == 0:
            self.sign = 0
        else:
            self.sign = (-1, 1)[p * q > 0]
        # valeurs initiales preservees
        self.__pInit = p
        self.__qInit = q
        self.initValues = [p, q]
        # on rend positives les valeurs
        # ce sont donc les valeurs de travail
        # attention elles sont variables !!
        # on gère le signe dans les operations +-*/
        self.__p = abs(p)
        self.__q = abs(q)
        # vérification de l'entrée
        self._intInputCheck()
        # 
        # Traitement
        # C'est ci-dessous que tout se passe
        # 
        self.__decalage = 0
        self._traitement()

    def _initFloat(self, d):
        sD = str(d)
        iVirgule = sD.find('.')
        puisDix = 10 ** (len(sD) - iVirgule - 1)
        self._initFraction(round(d * puisDix), puisDix)

    def _initStr(self, s):
        num = int(s)
        den = int("9" * len(s))
        self._initFraction(num, den)

####################################################################
####################################################################
    def _intInputCheck(self):
        try:
            assert self.__pInit == int(self.__pInit)
            assert self.__qInit == int(self.__qInit)
        except AssertionError:
            print('\nError: Use proper integers', self.__pInit, self.__qInit, '\n')
            sys.exit(os.EX_DATAERR)

####################################################################
####################################################################
    def __add__(self, d):
        """définition de l'addition
        utilisable avec le symbole + ainsi surchargé"""
        p, q = self.initValues
        try:
            # si d est un dvtDecimal
            pp, qq = d.initValues
        except AttributeError:
            # si d est un entier positif
            if int(d) == abs(d):
                pp, qq = d, 1
            else:
                raise ValueError("Impossible +: value is not int\
                nor dvtDecimal!")
        return dvtDecimal(p * qq + pp * q, q * qq)

    def __sub__(self, d):
        """voir addition"""
        p, q = self.initValues
        try:
            # si d est un dvtDecimal
            pp, qq = d.initValues
        except AttributeError:
            # si d est un entier positif
            if int(d) == abs(d):
                pp, qq = d, 1
            else:
                raise ValueError("Impossible -: value is not int\
                nor dvtDecimal!")
        return dvtDecimal(p * qq - pp * q, q * qq)

    def __mul__(self, d):
        """voir addition"""
        p, q = self.initValues
        try:
            # si d est un dvtDecimal
            pp, qq = d.initValues
        except AttributeError:
            # si d est un entier
            if abs(round(d)) == abs(d):
                pp, qq = d, 1
            else:
                raise ValueError("Impossible *: value is not int\
                nor dvtDecimal!")
        return dvtDecimal(p * pp, q * qq)

    def __truediv__(self, d):
        """voir addition"""
        p, q = self.initValues
        try:
            # si d est un dvtDecimal
            pp, qq = d.initValues
        except AttributeError:
            # si d est un entier positif
            if abs(round(d)) == abs(d):
                pp, qq = d, 1
            else:
                raise ValueError("Impossible /: value is not int\
                nor dvtDecimal!")
        return dvtDecimal(p * qq, pp * q)

    def __pow__(self, autre):
        p, q = self.initValues
        return dvtDecimal(p ** autre, q ** autre)

    def __radd__(self, autre):
        """si on additionne flottant/eniter + dvtDecimal"""
        return self.__add__(autre)

    def __rsub__(self, autre):
        """si on soustrait flottant/enter - dvtDecimal"""
        autre = self.__sub__(autre)
        return autre.__mul__(-1)

    def __rmul__(self, autre):
        """si on mulitplie flottant/enter - dvtDecimal"""
        return self.__mul__(dvtDecimal(autre))
####################################################################
####################################################################
    def _gcd(self):
        # on reprend les valeurs init
        a, b = self.__pInit, self.__qInit
        # on les rend positives
        a, b = abs(a), abs(b)
        if a > b:
            a, b = b, a
        while b != 0:
            a, b = b, a % b
        self.gcd = a
        # on renvoie une valeur positive
        return self.gcd

####################################################################
####################################################################
    def _puissance10(self):
        while self.__q // 10 == self.__q / 10:
            self.__decalage += 1
            self.__q /= 10

    def _enleve2(self):
        while self.__q % 2 == 0:
            self.__decalage += 1
            self.__q /= 2
            self.__p *= 5

    def _enleve5(self):
        while self.__q % 5 == 0:
            self.__decalage += 1
            self.__q /= 5
            self.__p *= 2

    def _calculPartiePeriodique(self, p, q):
        self.repPart = []
        resteInit = p
        reste = -1
        while reste != resteInit:
            p *= 10
            d = p // q
            p = p % q
            reste = p
            self.repPart.append(int(d))

####################################################################
####################################################################
    def irrPart(self):
        lpE = len(str(self.__pi))
        self.__nbZ = self.__decalage - lpE
        irr = "0."
        if self.__nbZ >= 0:
            for i in range(self.__nbZ):
                irr += "0"
            irr += str(self.__pi)
        return irr

    def mixedF(self):
        p, q = map(abs, self.simpValues)
        e = abs(self.intPart)
        return [e * self.sign, p - e * q, q]

    def repPartC(self):
        repPartCo = ''
        for d in self.repPart:
            repPartCo += str(d)
        return repPartCo

    def periodLen(self):
        return len(self.repPartC())


####################################################################
####################################################################
    def _traitement(self):
        # attention travail négatif potentiel
        self.simpValues = [k//self._gcd() for k in self.initValues]
        self.intPart = int(self.__pInit / self.__qInit)
        # valeurs positives requises pour le travail
        self.__p = abs(self.__pInit) - abs(self.__qInit) * abs(self.intPart)
        self.__p, self.__q = self.__p // self._gcd(), self.__q // self._gcd()
        # debut algo
        self._puissance10()
        self._enleve2()
        self._enleve5()
        self.__pi = int(self.__p // self.__q)
        self.__p = self.__p % self.__q
        # self._irrPart()
        self._calculPartiePeriodique(self.__p, self.__q)
        # fin algo
        #self._repPartC()
        #self._periodLen()
        #self._mixedF()
        #
        # pas de tolerance fixable pour la commande suivante
        # self._egyptG2()
        # cette tolérance sert pour la méthode egyptFractions
        # elle peut être changée dans le script
        self.tolerance = 1e-2

####################################################################
####################################################################
    def dispResults(self):
        print("For fraction:", self.fraction())
        print("    integer   part :", self.intPart)
        print("    irregular part :", self.irrPart())
        print("    periodic  part :", self.repPart)
        print("    mixed fraction :", self.mixedF())
        print("    simp. fraction :", self.simpValues)
        print("               gcd :", self.gcd)
        print("    Python outputs :", eval(self.fraction()))

    def __str__(self):
        p, q = self.simpValues
        reponse = ""
        if q == 1:
            reponse = str(p)
        else:
            reponse = str(p) + "/" + str(q)
        return reponse

    def __repr__(self):
        return self.__str__()

    # n est le nombre de chiffres apres la virgule
    def dotWrite(self, n):
        irr = str(self.irrPart())
        rpc = self.repPartC()
        resultat = str(self.intPart)
        # on compte les longueurs (apres la virgule)
        lpI = len(irr[2:])
        lpP = len(rpc)
        if n <= lpI:
            resultat += irr[1:n+2]
        elif n <= lpI+lpP:
            resultat += irr[1:] + rpc[:n-lpI]
        else:
            resultat += irr[1:]
            for i in range((n-lpI) // lpP):
                resultat += rpc
            resultat += rpc[:(n-lpI) % lpP]
        return resultat
   
    def isDecimal(self):
        return self.repPart == [0]

    def fraction(self):
        return str(self.__pInit) + "/" + str(self.__qInit)

    def toTeX(self):
        bs = "\\"
        f = "{" + str(self.__pInit) + bs + "over" + str(self.__qInit) + "}"
        e, p, q = self.mixedF()
        mF = "{" + str(e) + "\\raise.21em\hbox{$\\scriptscriptstyle\\frac{" + str(p) + "}{" + str(q) + "}$}}"
        #      
        eD = str(e) + str(self.irrPart()[1:]) + \
            r"\overline{" + str(self.repPartC()) + "}"
        return [f, mF, eD]

####################################################################
####################################################################
    # def __augmentation2(d, f, k, incr=1):
    #     d[k] += incr
    #     f[k + 1] = f[k] - 1 / d[k]
    #     if f[k+1] <= 1e-10:
    #         f[k+1] = 0
    #     return d, f

    # def egyptFractions2(self, eF=3, lim=10):
    #     """recherche d'une somme de fractions unitaires
    #     cf. fractions egyptiennes
    #     Par défaut somme de 3 fractions
    #     et un maximum de 10 solutions de sommes
    #     """
    #     #
    #     _, p, q = self.mixedF()
    #     #
    #     # initialisation
    #     solutions = []
    #     d = [0] * eF
    #     f = [0] * eF
    #     # début
    #     k = 0
    #     d[0] = 1 + int(q / p)
    #     f[0] = p / q
    #     f[1] = f[0] - 1 / d[0]
    #     c = 0
    #     c += 1
    #     print(c, d)
    #     # quand on revient en dessous de 0
    #     # c'est qu'on a trouvé toutes les
    #     # solutions potentielles
    #     while k > -1:
    #         # test d'existence du dénominateur
    #         # suivant
    #         if d[k] * f[k] >= eF - k:
    #             # ça n'a pas fonctionné, on change
    #             # le dénominateur précédent et on recalcule
    #             # la diff
    #             k -= 1
    #             if k > -1:
    #                 #d[k] += 1
    #                 #f[k + 1] = f[k] - 1 / d[k]
    #                 d, f = dvtDecimal.__augmentation2(d, f, k)
    #             c += 1
    #             print(c, d)
    #         # si on arrive sur l'avant-dernier
    #         elif k == eF - 2:
    #             # on teste si on a une solution
    #             # avec le dénominateur
    #             if f[eF - 1] >= 1e-10 and isInteger(1 / f[eF - 1]):
    #                 d[eF-1] = round(1 / f[eF-1])
    #                 # des solutions apparaissent qui n'en sont pas
    #                 # par exemple sur 3/8
    #                 # 1e8 un peu au hasard
    #                 if d[eF-1] <= 1e8:
    #                     solutions.append(d.copy())
    #             # sinon on augmente le dénominateur
    #             # et on recalcule la diff
    #             d, f = dvtDecimal.__augmentation2(d, f, k)
    #             c += 1
    #             print(c, d)
    #         else:
    #             # on augmente le dénominateur
    #             # on recalcule la diff.
    #             k += 1
    #             d[k] = 1 +max(d[k - 1], int(1 / f[k]))
    #             f[k + 1] = f[k] - 1 / d[k]
    #             #d, f = dvtDecimal.__augmentation2(d, f, k,
    #             #        1 + max(d[k - 1], int(1 / f[k])))
    #             c += 1
    #             print(c, d)
    #         if len(solutions) >= lim:
    #             break
    #     return solutions

    def __augmentation(d, f, k, incr=1):
        # !!! on incrémente ou on value
        d[k] = d[k] + incr if incr == 1 else incr
        f[k + 1] = f[k] - dvtDecimal(1, d[k])
        return d, f

    def egyptFractions(self, eF=3, lim=10):
        """recherche d'une somme de fractions unitaires
        cf. fractions egyptiennes
        Par défaut somme de 3 fractions
        et un maximum de 10 solutions de sommes
        """
        #
        _, p, q = self.mixedF()
        #
        # initialisation
        solutions = []
        d = [0] * eF
        f = [0] * eF
        unite = dvtDecimal(1, 1)
        # début
        k = 0
        d[0] = 1 + int(q / p)
        f[0] = dvtDecimal(p, q)
        temp = dvtDecimal(1, d[0])
        f[1] = f[0] - temp
        # quand on revient en dessous de 0
        # c'est qu'on a trouvé toutes les
        # solutions potentielles
        while k > -1:
            #print(d)
            # test d'existence du dénominateur
            # suivant
            g = f[k] * d[k]
            if float(g.dotWrite(0)) >= eF - k:
                # ça n'a pas fonctionné, on change
                # le dénominateur précédent et on recalcule
                # la diff
                k -= 1
                if k > -1:
                    #d[k] += 1
                    #f[k + 1] = f[k] - 1 / d[k]
                    d, f = dvtDecimal.__augmentation(d, f, k)
            # si on arrive sur l'avant-dernier
            elif k == eF - 2:
                # on teste si on a une solution
                # avec le dénominateur
                g = f[eF - 1]
                g = unite / g
                # soyons précis !
                #hN = float(h.dotWrite(15))
                #if float(g.dotWrite(0)) >= 1e-10 and \
                
                #if isInteger(hN, tolerance=0):
                if g.simpValues[1] == 1:
                    d[eF-1] = g.intPart
                    # des solutions apparaissent qui n'en sont pas
                    # par exemple sur 3/8
                    # 1e8 un peu au hasard
                    #if d[eF-1] <= 1e8:
                    solutions.append(d.copy())
                # sinon on augmente le dénominateur
                # et on recalcule la diff
                d, f = dvtDecimal.__augmentation(d, f, k)
                #d[k] += 1
                #f[k + 1] = f[k] - 1 / d[k]
            else:
                # on augmente le dénominateur
                # on recalcule la diff.
                k += 1
                g = unite / f[k]
                gN = float(g.dotWrite(0))
                aug = 1 + max(d[k - 1], round(gN))
                d, f = dvtDecimal.__augmentation(d, f, k, \
                        1 + max(d[k - 1], round(gN)))
                #
            if len(solutions) >= lim and lim != 0:
                break
            # try:
            #     del temp
            # except:
            #     pass
        del temp
        del g
        del unite
        del f
        return solutions

    def egyptG2(self):
        """recherche d'une somme de 2 fractions unitaires
        cf. fractions egyptiennes
        méthode glouton
        """
        #
        _, p, q = self.mixedF()
        #
        if p == 0:
            return []
        #
        soluce = []
        r = int(q / p) + 1
        s = q * r / (p * r - q)
        while r < s:
            if isInteger(s, tolerance=1e-5):
                soluce = [r, int(s)]
                break
            r += 1
            s = q * r / (p * r - q)
        return soluce

####################################################################
####################################################################

    def contFraction(self):
        p, q = self.simpValues
        f = []
        while q > 0:
            p, a, q = q, *divmod(p, q)
            f += [a]
        return f
