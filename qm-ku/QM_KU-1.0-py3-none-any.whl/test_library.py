#!/usr/bin/env python3
import QM as q
import numpy as np


def prop_associative(x, y, z):
    return np.all((x * y) * z == x * (y * z))


def prop_distributive(x, y, z):
    return np.all(x * (y + z) == (x * y) + (x * z))


def prop_identity(x):
    return np.all((1 * x) == x)


def prop_zero(x):
    return np.all((0 * x) == 0)


# Test the bra and ket class ########################################
x = q.bra([1, 3, 5])    # <x|
y = q.ket([4, 7, 2])    # |y>
z = q.bra([8, 4, 1])    # <z|

# Test the associative property
# ( <x||y> ) <z| = <x| ( |y><z| )
assert(prop_associative(x, y, z))

# Test distributive property
# <x| ( |y> + |z*> ) = <x||y> + <x||z*>
assert(prop_distributive(x, y, z.H))

# Test identity property
# 1 * <x| = <x|
assert(prop_identity(x))

# Test zero identity
# 0 * <x| = 0
assert(prop_zero(x))

# Test the operator class ###########################################
A = q.operator([[1, 3, 5], [2, 4, 7], [2, 9, 8]])
B = q.operator([[6, 3, 9], [0, 7, 2], [1, 9, 3]])
C = q.operator([[3, 6, 2], [8, 0, 4], [6, 8, 2]])

# Test the associative property
# (AB) C = A (B*C)
assert(prop_associative(A, B, C))

# Test distributive property
# A * (B + C) = AB + AC
assert(prop_distributive(A, B, C))

# Test identity property
# 1*A = A
assert(prop_identity(A))

# Test zero identity
# 0 * A = 0
assert(prop_zero(A))

# Test mixing of the classes ########################################

# Test the associative property
# ( <x|A ) |y> = <x| ( A|y> )
assert(prop_associative(x, A, y))

# Test distributive property
# <x| ( A + B ) = <x|A + <x|B
assert(prop_distributive(x, A, B))

# A ( |y> + |z*> ) = A|y> + A|z*>
assert(prop_distributive(A, y, z.H))

# Operator testing ##################################################
x *= 2
y += 3
z -= x
a = z*0
b = 0*z
A += B
A *= 2
A = A/2
A = -A

# Testing internal functions ########################################

# .prob()
assert(np.all(q.bra([1, 2, 3, 4]).prob() == [1, 4, 9, 16]))

# indexing
assert(isinstance(B[0], q.ket))

# Numpy function testing ############################################
# .all()
assert(q.bra([1, 1, 1, 1]).all())
assert(not q.bra([1, 1, 0, 1]).all())

# .any()
assert(q.bra([1, 1, 1, 1]).any())
assert(q.bra([1, 1, 0, 1]).any())
assert(not q.bra([0, 0, 0, 0]).any())

# .argmax()
assert(q.bra([1, 5, 2, 3]).argmax() == 1)

# .argmin()
assert(q.bra([1, 5, 2, 3]).argmin() == 0)

# .argsort()
assert(np.all(q.bra([1, 5, 2, 3]).argsort() == [0, 2, 3, 1]))

# .astype()
b = q.bra([1, 2, 3, 5])
assert(isinstance(b[0], np.int64))
b = b.astype(complex)
assert(isinstance(b[0], complex))

# .conj()
b = q.bra([1+1j, 2, 3, 5]).conj()
assert(b[0] == (1-1j))

# .conjugate()
b = q.bra([1+1j, 2, 3, 5]).conjugate()
assert(b[0] == (1-1j))

# .cumprod()
assert(np.all(q.ket([1, 2, 3]).cumprod() == [1, 2, 6]))

# .cumsum()
assert(np.all(q.ket([1, 2, 3]).cumsum() == [1, 3, 6]))

# .max()
assert(q.ket([1, 2, 3]).max() == 3)

# .mean()
assert(q.ket([1, 2, 3]).mean() == 2)

# .mean()
assert(q.ket([1, 2, 3]).min() == 1)

# .prod()
assert(q.ket([1, 2, 3]).prod() == 6)

# .round()
assert(np.all(q.bra([1.4, 2.7, 3.5]).round() == [1, 3, 4]))

# .sort()
b = q.bra([1.5, 3.5, 3.2])
b.sort()
assert(np.all(b == [1.5, 3.2, 3.5]))

# .std()
assert(q.bra([2, 4, 6]).std(ddof=1) == 2)

# .sum()
assert(q.bra([2, 4, 6]).sum() == 12)

# .tolist()
assert(isinstance(q.bra([2, 4, 6]).tolist(), list))

# .trace()
assert(q.operator([[2, 5, 8], [5, 0, 9], [3, 1, 9]]).trace() == 11)

# .transpose()
assert(isinstance(q.bra([1, 3, 5]).transpose(), q.ket))

# .var()
assert(q.bra([2, 4, 6]).var(ddof=1) == 4)

# Interaction with external numpy functions #########################

# np.sum()
assert(np.sum(q.bra([1,2,3])) == 6)
assert(isinstance(np.sum(q.bra([1,2,3])), np.int64))

# np.conj()
assert(all(np.conj(q.bra([1,2,3])) == q.bra([1,2,3])))
assert(isinstance(np.conj(q.bra([1,2,3])), q.bra))

# np.transpose()
assert(all(np.transpose(q.bra([1,2,3])) == q.ket([1,2,3])))
assert(isinstance(np.transpose(q.bra([1,2,3])), q.ket))

# np.diagonal()
assert(all(np.diagonal(q.ket([1,2,3])*q.bra([1,2,3])) == np.array([1,4,9])))
assert(isinstance(np.diagonal(q.ket([1,2,3])*q.bra([1,2,3])), np.ndarray))

# np.diag()
assert(all(np.diag(q.ket([1,2,3])*q.bra([1,2,3])) == np.array([1,4,9])))
assert(isinstance(np.diag(q.ket([1,2,3])*q.bra([1,2,3])), np.ndarray))

print('All tests passed')
