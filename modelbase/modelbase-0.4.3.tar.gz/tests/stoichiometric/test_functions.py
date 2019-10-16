# import unittest
# import numpy as np
# from modelbase.ode import Model as OdeModel
# from modelbase.stoichiometric import reduce_kinetic_model
#
#
# p = {
#     'l': 0.5,
#     'k1': 1,
#     'k2': 1,
#     'k3': 1,
#     'p': 0.5,
#     'tot': 1
# }
#
#
# def conrel(p, y):
#     return [p.tot - y]
#
#
# def v0(p, t, x):
#     "Time dependent stimulus"
#     return x * np.exp(-p.l * t)
#
#
# def k1(p, x, y0):
#     "Kinase"
#     return p.k1 * x * y0
#
#
# def k2(p, x, y0):
#     "Kinase"
#     return p.k2 * x * y0
#
#
# def phosph(p, x):
#     "Unspecific phosphatase"
#     return p.p * x
#
#
# m = OdeModel(p)
# m.add_compounds(['X', 'Y', 'Z'])
# m.add_algebraic_module('rapidEqx', conrel, ['X'], ['Xi'])
# m.add_algebraic_module('rapidEqy', conrel, ['Y'], ['Yi'])
# m.add_algebraic_module('rapidEqz', conrel, ['Z'], ['Zi'])
#
# m.add_reaction('v0', v0, {'X': 1}, ['time', 'Xi'])
# m.add_reaction('k1', k1, {'Y': 1}, ['X', 'Yi'])
# m.add_reaction('k2', k2, {'Z': 1}, ['Y', 'Zi'])
# m.add_reaction('p1', phosph, {'X': -1}, ['X'])
# m.add_reaction('p2', phosph, {'Y': -1}, ['Y'])
# m.add_reaction('p3', phosph, {'Z': -1}, ['Z'])
#
#
# class TestStoichiometricFunctions(unittest.TestCase):
#     def test_reduce_kinetic_model_compounds(self):
#         sm = reduce_kinetic_model(m)
#         equal = np.array_equal(sm.get_compounds(), ['X', 'Y', 'Z'])
#         self.assertTrue(equal)
#
#     def test_reduce_kinetic_model_reaction_names(self):
#         sm = reduce_kinetic_model(m)
#         equal = np.array_equal(sm.get_reaction_names(), ['v0', 'k1', 'k2', 'p1', 'p2', 'p3'])
#         self.assertTrue(equal)
#
#     def test_reduce_kinetic_model_stoichiometries(self):
#         expected = {'v0': {'X': 1}, 'k1': {'Y': 1}, 'k2': {'Z': 1}, 'p1': {'X': -1}, 'p2': {'Y': -1}, 'p3': {'Z': -1}}
#         sm = reduce_kinetic_model(m)
#         self.assertEqual(sm.get_stoichiometries(), expected)
