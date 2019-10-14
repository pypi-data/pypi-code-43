# to speed-up FDR, calculate ahead sum([1/i for i in range(1, m+1)]), for m in
# [1,100000]. For higher values of m use an approximation, with error less or
# equal to 4.99999157277e-006. (sum([1/i for i in range(1, m+1)])
# ~ log(m) + 0.5772..., 0.5572 is an Euler-Mascheroni constant)
import math

c = [1.0]
for m in range(2, 100000):
    c.append(c[-1] + 1.0/m)


def is_sorted(l):
    return all(l[i] <= l[i+1] for i in range(len(l)-1))


def FDR(p_values, dependent=False, m=None, ordered=False):
    """
    `False Discovery Rate
    <http://en.wikipedia.org/wiki/False_discovery_rate>`_
    correction on a list of p-values.

    Parameters
    ----------
    p_values : list
        List of p-values
    dependent : bool
        Use correction for dependent hypotheses (default False).
    m : int
        Number of hypotheses tested (default ``len(p_values)``).
    ordered : bool
        Prevent sorting of p-values if they are already sorted (default False).
    """

    if not ordered:
        ordered = is_sorted(p_values)

    if not ordered:
        joined = [(v, i) for i, v in enumerate(p_values)]
        joined.sort()
        p_values = [p[0] for p in joined]
        indices = [p[1] for p in joined]

    if not m:
        m = len(p_values)
    if m <= 0 or not p_values:
        return []

    if dependent: # correct q for dependent tests
        k = c[m-1] if m <= len(c) \
            else math.log(m) + \
                 0.57721566490153286060651209008240243104215933593992
        m = m * k

    tmp_fdrs = [p*m/(i+1.0) for (i, p) in enumerate(p_values)]
    fdrs = []
    cmin = tmp_fdrs[-1]
    for f in reversed(tmp_fdrs):
        cmin = min(f, cmin)
        fdrs.append( cmin)
    fdrs.reverse()

    if not ordered:
        new = [None] * len(fdrs)
        for v, i in zip(fdrs, indices):
            new[i] = v
        fdrs = new

    return fdrs
