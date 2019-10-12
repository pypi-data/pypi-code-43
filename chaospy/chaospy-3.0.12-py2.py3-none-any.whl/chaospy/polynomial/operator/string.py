"""
Polynomial string representation::

    >>> from chaospy.polynomial import npoly
    >>> print(npoly({(0,): 4, (1,): 6}))
    4+6q0
    >>> print(npoly({(0,): [1., 0., 3.], (1,): [0., -5., -1.]}))
    [1.0 -5.0q0 3.0-1.0q0]
    >>> print(npoly({
    ...     (0,): [[[1., 2.], [3., 4.]]], (1,): [[[4., 5.], [6., 7.]]]}))
    [[[1.0+4.0q0 2.0+5.0q0]
      [3.0+6.0q0 4.0+7.0q0]]]
"""
import numpy

VARNAME = "q"
POWER = "^"
SEP = ""


def construct_str_array(poly, sep=SEP, power=POWER, varname=VARNAME):
    if not poly.shape:
        output = []
        for exponents, coefficient in zip(
                poly.exponents.tolist(), poly.coefficients):

            if not coefficient:
                continue

            out = ""
            if coefficient != 1 or not any(exponents):
                out = str(coefficient)

            for idx, exponent in enumerate(exponents):
                if exponent:
                    if out:
                        out += sep
                    out += varname+str(idx)
                if exponent > 1:
                    out += power+str(exponent)
            if output and float(coefficient) >= 0:
                out = "+"+out
            output.append(out)

        if output:
            return "".join(output)
        return str(numpy.zeros(1, dtype=poly._dtype).item())

    return [
        construct_str_array(poly_, sep=sep, power=power, varname=varname)
        for poly_ in poly
    ]
