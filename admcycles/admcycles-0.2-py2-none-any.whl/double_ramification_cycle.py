r"""
Double ramification cycle
"""

from __future__ import absolute_import, print_function
from six.moves import range
from admcycles.admcycles import Tautv_to_tautclass, Tautvb_to_tautclass, Tautvecttobasis, tautgens, psiclass, tautclass
from admcycles.stable_graph import StableGraph
import admcycles.DR as DR

import itertools
from copy import deepcopy

from sage.combinat.subset import Subsets
from sage.arith.all import factorial
from sage.functions.other import floor, ceil
from sage.misc.misc_c import prod
from sage.rings.all import PolynomialRing, QQ, ZZ
from sage.modules.free_module_element import vector
from sage.rings.polynomial.polynomial_ring import polygen
from sage.rings.polynomial.multi_polynomial_element import MPolynomial

############
#
# Old DR-cycle implementation
#
############


def DR_cycle_old(g, Avector, d=None, k=None, tautout=True, basis=False):
    r"""Returns the k-twisted Double ramification cycle in genus g and codimension d
    for the partition Avector of k*(2g-2+n).

    In the notation of the [JPPZ]-paper, the output is 2^(-d) * P_g^{d,k}(Avector).

    Note: This is based on the old implementation DR_compute by Pixton. A new one,
    which can be faster in many examples is DR_cycle.

    INPUT:

    - ``tautout` -- bool (default: `True`); if False, returns a vector
      (in all generators for basis=false, in the basis of the ring for basis=true)

    - ``basis`   -- bool (default: `False`); if True, use FZ relations to give out the
      DR cycle in a basis of the tautological ring
    """
    if d is None:
        d = g
    n = len(Avector)    
    if k is None:
        k = floor(sum(Avector)/(2*g-2+n))
    if sum(Avector) != k*(2*g-2+n):
        raise ValueError('2g-2+n must divide the sum of entries of Avector.')

    v = DR.DR_compute(g, d, n, Avector, k)
    v1 = vector([QQ(a) for a in DR.convert_vector_to_monomial_basis(v, g, d, tuple(range(1, n+1)), DR.MODULI_ST)])

    if basis:
        v2 = Tautvecttobasis(v1, g, n, d)
        if tautout:
            return Tautvb_to_tautclass(v2, g, n, d)
        else:
            return v2
    else:
        if tautout:
            return Tautv_to_tautclass(v1, g, n, d)
        else:
            return v1


############
#
# New DR-cycle implementation
#
############

def DR_cycle(g, Avector, d=None, k=None, rpoly=False, tautout=True, basis=False):
    r"""Returns the k-twisted Double ramification cycle in genus g and codimension d
    for the partition Avector of k*(2g-2+n). If some elements of Avector are elements of a
    polynomial ring, compute DR-polynomial and substitute the entries of Avector - the result
    then has coefficients in a polynomial ring.

    In the notation of the [JPPZ]-paper, the output is 2^(-d) * P_g^{d,k}(Avector).

    Note: This is a reimplementation of Pixton's DR_compute which can be faster in many examples.
    To access the old version, use DR_cycle_old - it might be faster on older SageMath-versions.

    INPUT:

    - ``rpoly``  -- bool (default: `False`); if True, return tautclass 2^(-d) * P_g^{d,r,k}(Avector)
      whose coefficients are polynomials in the variable r.

    - ``tautout` -- bool (default: `True`); if False, returns a vector
      (in all generators for basis=false, in the basis of the ring for basis=true)

    - ``basis`   -- bool (default: `False`); if True, use FZ relations to give out the
      DR cycle in a basis of the tautological ring

    EXAMPLES::

      sage: from admcycles import DR_cycle, DR_cycle_old
      sage: DR_cycle(1, (2, 3, -5))
      Graph :      [1] [[1, 2, 3]] []
      Polynomial : 2*psi_1^1
      <BLANKLINE>
      Graph :      [1] [[1, 2, 3]] []
      Polynomial : 9/2*psi_2^1
      <BLANKLINE>
      Graph :      [1] [[1, 2, 3]] []
      Polynomial : 25/2*psi_3^1
      <BLANKLINE>
      Graph :      [0, 1] [[2, 3, 5], [1, 6]] [(5, 6)]
      Polynomial : (-2)*
      <BLANKLINE>
      Graph :      [0, 1] [[1, 3, 5], [2, 6]] [(5, 6)]
      Polynomial : (-9/2)*
      <BLANKLINE>
      Graph :      [0, 1] [[1, 2, 5], [3, 6]] [(5, 6)]
      Polynomial : (-25/2)*
      <BLANKLINE>
      Graph :      [0] [[5, 6, 1, 2, 3]] [(5, 6)]
      Polynomial : (-1/24)*
      sage: D = DR_cycle(1, (1, 3, -4), d=2)
      sage: D2 = DR_cycle_old(1, (1, 3, -4), d=2)  # long time
      sage: D.toTautvect() == D2.toTautvect()     # long time
      True
      sage: D.is_zero() # Clader-Janda: P_g^{d,k}(Avector)=0 for d>g
      True
      sage: v = DR_cycle(2, (3,), d=4, rpoly=true).evaluate()
      sage: v  # Conjecture by Longting Wu predicts that r^1-term vanishes
      -1/1728*r^6 + 1/576*r^5 + 37/34560*r^4 - 13/6912*r^3 - 1/1152*r^2
      
    We can create a polynomial ring and use an Avector with entries in this ring.
    The result is a tautological class with polynomial coefficients::
      
      sage: R.<a1,a2>=PolynomialRing(QQ,2)
      sage: Q=DR_cycle(1,(a1,a2,-a1-a2))
      sage: Q
      Graph :      [1] [[1, 2, 3]] []
      Polynomial : 1/2*a1^2*psi_1^1 
      <BLANKLINE>
      Graph :      [1] [[1, 2, 3]] []
      Polynomial : 1/2*a2^2*psi_2^1 
      <BLANKLINE>
      Graph :      [1] [[1, 2, 3]] []
      Polynomial : (1/2*a1^2 + a1*a2 + 1/2*a2^2)*psi_3^1 
      <BLANKLINE>
      Graph :      [0, 1] [[2, 3, 5], [1, 6]] [(5, 6)]
      Polynomial : (-1/2*a1^2)*
      <BLANKLINE>
      Graph :      [0, 1] [[1, 3, 5], [2, 6]] [(5, 6)]
      Polynomial : (-1/2*a2^2)*
      <BLANKLINE>
      Graph :      [0, 1] [[1, 2, 5], [3, 6]] [(5, 6)]
      Polynomial : (-1/2*a1^2 - a1*a2 - 1/2*a2^2)*
      <BLANKLINE>
      Graph :      [0] [[5, 6, 1, 2, 3]] [(5, 6)]
      Polynomial : (-1/24)*
      

    TESTS::

      sage: from admcycles import DR_cycle, DR_cycle_old
      sage: D = DR_cycle(2, (3, 4, -2), k=1)       # long time
      sage: D2 = DR_cycle_old(2, (3, 4, -2), k=1)  # long time
      sage: D.toTautvect() == D2.toTautvect()      # long time
      True
      sage: D = DR_cycle(2, (1, 4, 5), k=2)        # long time
      sage: D2 = DR_cycle_old(2, (1, 4, 5), k=2)   # long time
      sage: D.toTautvect() == D2.toTautvect()      # long time
      True
      sage: D = DR_cycle(3, (2,4), k=1)            # long time
      sage: D2 = DR_cycle_old(3, (2,4), k=1)       # long time
      sage: D.toTautvect() == D2.toTautvect()      # long time
      True

      sage: D = DR_cycle(2, (3,),tautout=False); D
      (0, 1/8, -9/4, 81/8, 1/4, -9/4, -1/8, 1/8, 1/4, -1/8, 1/48, 1/240, -3/16, -41/240, 1/48, 1/48, 1/1152)
      sage: D2=DR_cycle_old(2, (3,), tautout=False); D2
      (0, 1/8, -9/4, 81/8, 1/4, -9/4, -1/8, 1/8, 1/4, -1/8, 1/48, 1/240, -3/16, -41/240, 1/48, 1/48, 1/1152)
      sage: D3 = DR_cycle(2, (3,), tautout=False, basis=True); D3
      (-5, 2, -8, 18, 3/2)
      sage: D4 = DR_cycle_old(2, (3,), tautout=False, basis=True); D4
      (-5, 2, -8, 18, 3/2)
    """
    if d is None:
        d = g
    n = len(Avector)
    
    if any(isinstance(ai,MPolynomial) for ai in Avector):
        # compute DRpoly and substitute the ai in there
        pol, gens = DRpoly(g, d, n, tautout=tautout, basis=basis, gensout=True)
        subsdict={gens[i] : Avector[i] for i in range(n)}
        
        if tautout:
            pol.coeff_subs(subsdict)
            pol.simplify()
            return pol
        else:
            return pol.apply_map(lambda x: x.subs(subsdict))
    
    if k is None:
        k = floor(sum(Avector)/(2*g-2+n))
    if sum(Avector) != k*(2*g-2+n):
        raise ValueError('2g-2+n must divide the sum of entries of Avector.')

    gens = tautgens(g, n, d, decst=True)
    v = vector([DR_coeff_new(decs, g, n, d, Avector, k, rpoly) for decs in gens]) / ZZ(2)**d
    #v1=vector([QQ(a) for a in DR.convert_vector_to_monomial_basis(v,g,d,tuple(range(1, n+1)),DR.MODULI_ST)])

    if basis:
        v1 = Tautvecttobasis(v, g, n, d)
        if tautout:
            return Tautvb_to_tautclass(v1, g, n, d)
        else:
            return v1
    else:
        if tautout:
            return Tautv_to_tautclass(v, g, n, d)
        else:
            return v


def interpolate(A, B):
    r"""
    Univariate Lagrange interpolation over the rationals.

    EXAMPLES::

        sage: from admcycles.double_ramification_cycle import interpolate
        sage: p = interpolate([1/2, -2, 3], [4/5, 2/3, -7/6])
        sage: p(1/2)
        4/5
        sage: p(-2)
        2/3
        sage: p(3)
        -7/6

    TESTS::

        sage: from admcycles.double_ramification_cycle import interpolate
        sage: parent(interpolate([], []))
        Univariate Polynomial Ring in r over Rational Field
    """
    R = polygen(QQ, 'r').parent()
    return R.lagrange_polynomial(zip(A, B))


def DR_coeff_setup(G, g, n, d, Avector, k):
    gamma = G.gamma
    kappa, psi = G.poly.monom[0]
    exp_list = []
    scalar_factor = QQ((1, G.automorphism_number()))
    given_weights = [-k*(2*gv - 2 + len(gamma.legs[i])) for i,gv in enumerate(gamma.genera)]

    # contributions to scalar_factor from kappa-classes
    for v in range(len(gamma.genera)):
        if len(kappa[v]) == 1: # some kappa_1^e at this vertex
            scalar_factor *= (-k**2)**(kappa[v][0]) / factorial(kappa[v][0])

    # contributions to scalar_factor and given_weights from markings
    for i in range(1, n+1):
        v = gamma.vertex(i)
        psipow = psi.get(i,0) # if i in dictionary, have psi_i^(psi[i]), otherwise have psi_i^0
        given_weights[v] += Avector[i-1]
        scalar_factor *= (Avector[i-1])**(2*psipow) / factorial(psipow)

    # contributions to scalar_factor and explist from edges
    for (lu, lv) in gamma.edges:
        psipowu = psi.get(lu, 0)
        psipowv = psi.get(lv, 0)
        exp_list.append(psipowu + psipowv + 1)
        scalar_factor *= ((-1)**(psipowu+psipowv)) / factorial(psipowv) / factorial(psipowu) / (psipowu+psipowv+1)

    return exp_list, given_weights, scalar_factor


def DR_coeff_new(G, g, n, d, Avector, k, rpoly):
    gamma = G.gamma # underlying stable graph of decstratum G
    kappa, psi = G.poly.monom[0]
    # kappa is a list of lenght = # vertices, of entries like [3,0,2] meaning that at this vertex there is a kappa_1^3 * kappa_3^2
    # psi is a dictionary and psi[3]=4 means there is a decoration psi^4 at marking/half-edge 3

    if any(len(kalist) > 1 for kalist in kappa):
        return 0  # vertices can only carry powers of kappa_1, no higher kappas allowed

    m0 = ceil(sum([abs(i) for i in Avector]) / ZZ(2)) + g*abs(k) # value from which on the Pixton-sum below will be polynomial in m
    h0 = len(gamma.edges) - len(gamma.genera) + 1 # first Betti number of the graph Gamma
    exp_list, given_weights, scalar_factor = DR_coeff_setup(G, g, n, d, Avector, k)

    deg = 2 * sum(exp_list)  # degree of polynomial in m
    # R = PolynomialRing(QQ, len(gamma.edges) + 1, 'd')
    # P=prod([(di*(d0-di))**exp_list[i] for i,di in enumerate(R.gens()[1:])])/(d0**h0)
    u = gamma.flow_solve(given_weights)
    Vbasis = gamma.cycle_basis()

    #mpoly = mpoly_affine_sum(P, u, Vbasis,m0+1,deg)
    mpoly = mpoly_special(exp_list, h0, u, Vbasis, m0+1, deg)

    # mpoly = interpolate(mrange, mvalues)
    if rpoly:
        return mpoly * scalar_factor
    else:
        return mpoly.subs(r=0) * scalar_factor


def mpoly_special(exp_list, h0, u, Vbasis, start, degr):
    r"""
    Return the sum of the rational function in DR_coeff_new over the
    affine space u + V modulo r in ZZ^n as a univariate polynomial in r.
    V is the lattice with basis Vbasis.
    Use that this sum is polynomial in r starting from r=start and the polynomial has
    degree degr (for now).
    """
    mrange = list(range(start, start + degr + 2))
    mvalues = []
    rank = len(Vbasis)
    ulen = len(u)

    for m in mrange:
        total = 0
        for coeff in itertools.product(*[list(range(m)) for i in range(rank)]):
            v = u + sum([coeff[i]*Vbasis[i] for i in range(rank)])
            v = [vi % m for vi in v]
            total += prod([(v[i]*(m-v[i]))**exp_list[i] for i in range(ulen)])
        mvalues.append(total/QQ(m**h0))

    return interpolate(mrange, mvalues)


def mpoly_affine_sum(P, u, Vbasis, start, degr):
    r"""
    Return the sum of the polynomial P in variables r, d1, ..., dn over the
    affine space u + V modulo r in ZZ^n as a univariate polynomial in r.
    V is the lattice with basis Vbasis.
    Use that this sum is polynomial in r starting from r=start and the polynomial has
    degree degr (for now).
    """
    mrange = list(range(start, start + degr + 2))
    mvalues = []
    rank = len(Vbasis)

    for m in mrange:
        total = 0
        for coeff in itertools.product(*[list(range(m)) for i in range(rank)]):
            v = u+sum([coeff[i]*Vbasis[i] for i in range(rank)])
            v = [vi % m for vi in v]
            total += P(m,*v)
        mvalues.append(total)

    return interpolate(mrange, mvalues)

############
#
# DR polynomial
#
############


def multivariate_interpolate(f, d, n, gridwidth=1, R=None, generator=None):
    r"""Takes a vector/number-valued function f on n variables and interpolates it on a grid around 0.
    Returns a vector with entries in a polynomial ring.

    INPUT:

    - ``d``        -- integer; maximal degree of output-polynomial in any of the variables

    - ``gridwidth` -- integer (default: `1`); width of the grid used for interpolation

    - ``R`         -- polynomial ring (default: `None`); expected to be polynomial ring in
      at least n variables; if None, use ring over QQ in variables z0,...,z(n-1)

    - ``generator` -- list (default: `None`); list of n variables in the above polynomial
      ring to be used in output; if None, use first n generators of ring

    EXAMPLES::

        sage: from admcycles.double_ramification_cycle import multivariate_interpolate
        sage: from sage.modules.free_module_element import vector
        sage: def foo(x,y):
        ....:     return vector((x**2+y,2*x*y))
        ....:
        sage: multivariate_interpolate(foo,2,2)
        (z0^2 + z1, 2*z0*z1)
    """
    if R is None:
        R = PolynomialRing(QQ,'z',n)
    if generator is None:
        generator = R.gens()

    if n == 0: # return constant
        return R.one()*f()

    points = itertools.product(*[[j for j in range(d+1)] for i in range(n)])
    # shift cube containing evaluation points in negative direction to reduce abs value of evaluation points
    shift = floor((d+1)/QQ(2))*gridwidth
    result = 0

    for p in points:
        # compute Lagrange polynomial not vanishing exactly at gridwidth*p
        lagr = prod([prod([generator[i]-(j*gridwidth-shift) for j in range(d+1) if j != p[i]]) for i in range(n)])
        pval = [gridwidth*coord-shift for coord in p]
        #global fex,lagrex, pvalex
        #fex=f
        #lagrex=lagr
        #pvalex=pval
        value = lagr.subs({generator[i]:pval[i] for i in range(n)})
        if n == 1: # avoid problems with multiplication of polynomial with vector
            mult = lagr/value
            result += vector((e*mult for e in f(*pval)))
        else:
            result += f(*pval) / value * lagr
    return result


def DRpoly(g, d, n, dplus=0, tautout=True, basis=False, ring=None, gens=None, gensout=False):
    r"""
    Return the Double ramification cycle in genus g with n markings in degree d as a
    tautclass with polynomial coefficients. Evaluated at a point (a_1, ..., a_n) with
    sum a_i = k(2g-2+n) it equals DR_cycle(g,(a_1, ..., a_n),d).

    The computation uses interpolation and the fact that DR is a polynomial in the a_i
    of degree 2*d.

    INPUT:

    - ``dplus``  -- integer (default: `0`); if dplus>0, the interpolation is performed
      on a larger grid as a consistency check

    - ``tautout` -- bool (default: `True`); if False, returns a polynomial-valued vector
      (in all generators for basis=false, in the basis of the ring for basis=true)

    - ``basis`   -- bool (default: `False`); if True, use FZ relations to give out the
      DR cycle in a basis of the tautological ring

    - ``ring`    -- polynomial ring (default: `None`); expected to be polynomial ring in
      at least n variables; if None, use ring over QQ in variables a1,...,an

    - ``gens`    -- list (default: `None`); list of n variables in the above polynomial
      ring to be used in output; if None, use first n generators of ring

    - ``gensout` -- bool (default: `False`); if True, return (DR polynomial, list of generators
      of coefficient ring)

    EXAMPLES::

      sage: from admcycles import DRpoly, DR_cycle, psiclass
      sage: D, (a1, a2) = DRpoly(1, 1, 2, gensout=True)
      sage: D.coeff_subs({a2:-a1}).simplify()
      Graph :      [1] [[1, 2]] []
      Polynomial : 1/2*a1^2*psi_1^1
      <BLANKLINE>
      Graph :      [1] [[1, 2]] []
      Polynomial : 1/2*a1^2*psi_2^1
      <BLANKLINE>
      Graph :      [0] [[4, 5, 1, 2]] [(4, 5)]
      Polynomial : (-1/24)*
      sage: (D*psiclass(1,1,2)).evaluate() # intersection number with psi_1
      1/24*a1^2 - 1/24
      sage: (D.coeff_subs({a1:4})-DR_cycle(1,(4,-4))).is_zero() # polynomial agrees with DR_cycle at (4,-4)
      True
      sage: DRpoly(1,2,2).is_zero() # Clader-Janda: DR vanishes in degree d>g
      True

    TESTS::

      sage: R.<a1,a2,a3,b1,b2,b3> = PolynomialRing(QQ, 6)
      sage: D = DRpoly(1, 1, 3, ring=R, gens=[a1, a2, a3])
      sage: Da = deepcopy(D)
      sage: Db = deepcopy(D).coeff_subs({a1:b1, a2:b2, a3:b3})
      sage: Dab = deepcopy(D).coeff_subs({a1:a1+b1, a2:a2+b2, a3:a3+b3})
      sage: diff = Da*Db - Da*Dab    # this should vanish in compact type by [Holmes-Pixton-Schmitt]
      sage: diff.toTautbasis(moduli='ct')
      (0)
    """
    def f(*Avector):
        return DR_cycle(g, Avector, d, tautout=False, basis=basis)
        #k=floor(QQ(sum(Avector))/(2 * g - 2 + n))
        #return vector([QQ(e) for e in DR_red(g,d,n,Avector, k, basis)])
        #return vector(DR_compute(g,d,n,Avector, k))

    if ring is None:
        ring = PolynomialRing(QQ, ['a%s'%i for i in range(1, n+1)])
    if gens is None:
        gens = ring.gens()[0:n]

    gridwidth = 2*g - 2 + n
    interp = multivariate_interpolate(f, 2*d + dplus, n, gridwidth, R=ring, generator=gens)

    if not tautout:
        ans = interp
    else:
        if not basis:
            ans = Tautv_to_tautclass(interp, g, n, d)
        else:
            ans = Tautvb_to_tautclass(interp, g, n, d)
    if gensout:
        return (ans, gens)
    else:
        return ans


def degree_filter(polyvec, d):
    r"""Takes a vector of polynomials in several variables and returns a vector containing the (total)
    degree d part of these polynomials.

    EXAMPLES::

        sage: from admcycles.double_ramification_cycle import degree_filter
        sage: R.<x,y> = PolynomialRing(QQ, 2)
        sage: v = vector((x+y**2+2*x*y,1+x**3+x*y))
        sage: degree_filter(v, 2)
        (2*x*y + y^2, x*y)
    """
    resultvec = deepcopy(polyvec)
    for i in range(len(polyvec)):
        s = 0
        for (c,m) in polyvec[i]:
            if m.degree() == d:
                s += c*m
        resultvec[i] = s
    return resultvec


def Hain_divisor(g, A):
    r"""
    Returns a divisor class D extending the pullback of the theta-divisor under the Abel-Jacobi map (on compact type) given by partition A of zero.
    Note: D^g/g! agrees with the Double-Ramification cycle in compact type.

    EXAMPLES::

      sage: from admcycles import *

      sage: R = PolynomialRing(QQ, 'z', 3)
      sage: z0, z1, z2 = R.gens()
      sage: u = Hain_divisor(2, (z0, z1, z2))
      sage: g = DRpoly(2, 1, 3, ring=R, gens=[z0, z1, z2]) #u,g should agree inside compact type
      sage: (u.toTautvect() - g.toTautvect()).subs({z0: -z1-z2})
      (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1/24)
    """
    n = len(A)

    def delt(l, g, n, I):
        # takes genus l and subset I of markings 1,...,n and returns generalized boundary divisor Delta_{l,I}
        I = set(I)
        if l == 0 and len(I) == 1:
            return -psiclass(list(I)[0],g,n)
        if l == g and len(I) == n-1:
            i_set = set(range(1, n+1)) - I
            return -psiclass(list(i_set)[0],g,n)
        if (l == 0 and len(I) == 0) or (l == g and len(I) == n):
            return tautclass([])

        Icomp = set(range(1, n+1)) - I
        gra = StableGraph([l,g-l], [list(I) + [n+1], list(Icomp) + [n+2]], [(n+1, n+2)])
        return QQ((1, gra.automorphism_number())) * gra.to_tautclass()

    result= QQ((-1, 4)) * sum([sum([(sum([A[i-1] for i in I])**2) * delt(l,g,n,I) for I in Subsets(list(range(1, n+1)))]) for l in range(0, g+1)])
    # note index i-1 since I subset {1,...,n} but array indices subset {0,...,n-1}

    return result
