'''Formulate reduced GROG training as mixed integer programming.'''

from time import time

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree # pylint: disable=E0611
from phantominator import radial

# if __name__ == '__main__':

t0 = time()

# Radial sampling coordinates
N = 4
kx, ky = radial(N, N)
kx = np.reshape(kx, (N, N)).flatten('F')
ky = np.reshape(ky, (N, N)).flatten('F')

# Cartesian grid
tx, ty = np.meshgrid(
    np.linspace(np.min(kx), np.max(kx), N),
    np.linspace(np.min(ky), np.max(ky), N))
tx, ty = tx.flatten(), ty.flatten()
outside = np.argwhere(
    np.sqrt(tx**2 + ty**2) > np.max(kx)).squeeze()
inside = np.argwhere(
    np.sqrt(tx**2 + ty**2) <= np.max(kx)).squeeze()
tx = np.delete(tx, outside)
ty = np.delete(ty, outside)
txy = np.concatenate((tx[:, None], ty[:, None]), axis=-1)

print('Took %g seconds to load coordinates' % (time() - t0))

# Desired shifts
t0 = time()
kxy = np.concatenate((kx[:, None], ky[:, None]), axis=-1)
kdtree = cKDTree(kxy)
_, idx = kdtree.query(txy, k=1)
dx, dy = tx - kx[idx], ty - ky[idx]
print('Took %g seconds to find shifts' % (time() - t0))

    # # plt.scatter(dx, dy)
    # plt.plot(np.diff(np.sort(np.abs(dx))))
    # plt.plot(np.diff(np.sort(np.abs(dy))))
    # plt.show()

    # from scipy.optimize import basinhopping
    # def _obj(x, K, p):
    #     N = p.size
    #     d = x[:K]
    #     A = np.around(x[K:K+N*K]).reshape((N, K))
    #     val = np.linalg.norm(A @ d - p)
    #     print(val)
    #     return val
    # K = dx.size
    # x0 = np.zeros((K + K*dx.size))
    # res = basinhopping(
    #     _obj, x0, T=5, stepsize=100, minimizer_kwargs={'args': (K, dx)})
    # print(res)

# print('N=%d' % dx.size)
#
# for ii, dx0 in enumerate(dx):
#     print('%d %.52f ' % (ii, dx0), end='')

# Mixed integer quadratic programming
udx = np.unique(np.abs(dx))
N = udx.size
K0 = udx.size
print(N, K0)

from pyomo.environ import (
    AbstractModel, Param, NonNegativeIntegers, Var, Reals, RangeSet,
    Constraint, Objective, summation, SolverFactory, value,
    minimize, Integers)

model = AbstractModel()
model.m = Param(within=NonNegativeIntegers, default=K0)
model.n = Param(within=NonNegativeIntegers, default=N)
model.I = RangeSet(0, model.m-1)
model.J = RangeSet(0, model.n-1)

model.p = Param(model.J, default=udx.tolist())

model.A = Var(model.I, model.J, domain=Integers)
model.d = Var(model.I, domain=Reals)

def ax_constraint_rule(model, i, j):
    '''return the expression for the constraint for i'''
    return sum(sum(model.A[i, j]*model.d[i] for i in model.I) - model.p[j] for j in model.J) >= 0
model.AxbConstraint = Constraint(model.I, model.J, rule=ax_constraint_rule)


def obj_expression(model):
    val = sum(sum(model.A[i, j]*model.d[i] for i in model.I) - model.p[j] for j in model.J)
    # val = sum(model.d[i] for i in model.I)
    return val

model.OBJ = Objective(rule=obj_expression, sense=minimize)

instance = model.create_instance()
# instance.pprint()

opt = SolverFactory('cplex')
opt.options['optimalitytarget'] = 3
results = opt.solve(instance, tee=True)
print(results)
# instance.load(results)

# Get A
A = np.zeros((K0, N))
for ii in range(K0):
    for jj in range(N):
        A[ii, jj] = value(instance.A[0, 1])

import matplotlib.pyplot as plt
plt.imshow(A)
plt.show()
# model.display()


    # # Mixed integer programming
    # from mip.model import Model, xsum
    # from mip.constants import CONTINUOUS, INTEGER
    # done = False
    # K0 = dx.size
    # while not done:
    #     print('TRYING K0=%d' % K0)
    #     m = Model()
    #
    #     # Variables to solve for
    #     d = [m.add_var(var_type=CONTINUOUS) for ii in range(K0)]
    #     y = []
    #     for ii in range(N):
    #         y.append([m.add_var(var_type=INTEGER) for jj in range(K0)])
    #
    #         # Constraints
    #         m += xsum(y[ii][jj] for jj in range(K0)) >= 0
    #         m += xsum(y[ii][jj]*d[jj] for jj in range(K0)) == dx[ii]
    #
    #         # Objective
    #         # print([y[ii][jj].x for jj in range(K0)])
    #         # m += xsum(y[ii][jj]*d[jj] for jj in range(K0)) - dx[ii]
    #
    #     # print(m)
    #     # assert False
    #     res = m.optimize()
    #     print(res)
