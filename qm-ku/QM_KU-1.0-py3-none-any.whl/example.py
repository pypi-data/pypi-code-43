#!/usr/bin/env python3

import QM as q
import numpy

# Create a bra and a ket using lists
v = q.bra([1, 2, 3, 4])
u = q.ket([4, 1, 2, 9])

# You can also create bra and ket using numpy arrays
w = q.bra(numpy.array([1, 2, 3, 4]))

# Use print to see the new output
print('print() on a bra outputs:')
print(v)
print('')
print('print() on a ket outputs:')
print(u)
print('')

# Perform arithmitic using bra and ket
print('Testing arithmitic')
print('v*u = <v||u> =')
print(v*u)
print('')

print('u*v = |u><v| = ')
print(u*v)
print('')

print('v*v.H = <v||v*> = ')
print(v*v.H)
print('')

print('|u|^2 = ')
print(u.prob())
print('')

A = u*v
print('eig(|u><v|) = ')
l, U = A.eig()
print(l)
print(U)
print(U[1])
print('')

# Numpy functions work directly with the objects
print('Testing numpy interaction')
print('numpy.shape(v)')
print(numpy.shape(v))
print('')

print('numpy.linalg.norm(u)')
print(numpy.linalg.norm(u))
print('')

print('The diagonal of |u><v|:')
print(numpy.diag(A))