# import unittest
# import numpy as np
# from modelbase.stoichiometric import Model
#
#
# class TestStoichiometricModel(unittest.TestCase):
#
#     def test_add_compounds(self):
#         m = Model()
#         m.add_compounds(['x', 'y', 'z'])
#         self.assertEqual(m._compounds, {'x': 0, 'y': 1, 'z': 2})
#
#     def test_get_compounds(self):
#         m = Model()
#         m.add_compounds(['x', 'y', 'z'])
#         self.assertEqual(m.get_compounds(), ['x', 'y', 'z'])
#
#     def test_add_reaction(self):
#         m = Model()
#         m.add_compounds(['x'])
#         m.add_reaction('v1', {'x': 1}, 0, 1000)
#         self.assertEqual(m._reactions, {'v1': {'stoichiometry': {'x': 1}, 'bounds': (0, 1000)}})
#
#     def test_get_reaction_names(self):
#         m = Model()
#         m.add_compounds(['x', 'y'])
#         m.add_reaction('v1', {'x': 1}, 0, 1000)
#         m.add_reaction('v2', {'x': -1, 'y': 1}, 0, 1000)
#         self.assertEqual(m.get_reaction_names(), ['v1', 'v2'])
#
#     def test_get_reaction_bounds(self):
#         m = Model()
#         m.add_compounds(['x', 'y'])
#         m.add_reaction('v1', {'x': 1}, 0, 1000)
#         m.add_reaction('v2', {'x': -1, 'y': 1}, 0, 1000)
#         self.assertEqual(m.get_reaction_bounds('v1'), (0, 1000))
#
#     def test_get_all_reaction_bounds(self):
#         m = Model()
#         m.add_compounds(['x', 'y'])
#         m.add_reaction('v1', {'x': 1}, 0, 1000)
#         m.add_reaction('v2', {'x': -1, 'y': 1}, 0, 1000)
#         m.get_reaction_bounds()
#         self.assertEqual(m.get_reaction_bounds(), {'v1': (0, 1000), 'v2': (0, 1000)})
#
#     def test_get_stoichiometries(self):
#         expected = {'v1': {'x': 1}, 'v2': {'x': -1, 'y': 1}, 'v3': {'y': -1}}
#         m = Model()
#         m.add_compounds(['x', 'y'])
#         m.add_reaction('v1', {'x': 1}, 0, 1000)
#         m.add_reaction('v2', {'x': -1, 'y': 1}, 0, 1000)
#         m.add_reaction('v3', {'y': -1}, 0, 1000)
#         self.assertEqual(m.get_stoichiometries(), expected)
#
#     def test_get_stoichiometry_matrix(self):
#         expected = np.array([[1., -1.,  0.],
#                              [0.,  1., -1.]])
#         m = Model()
#         m.add_compounds(['x', 'y'])
#         m.add_reaction('v1', {'x': 1}, 0, 1000)
#         m.add_reaction('v2', {'x': -1, 'y': 1}, 0, 1000)
#         m.add_reaction('v3', {'y': -1}, 0, 1000)
#         equal = np.array_equal(m.get_stoichiometry_matrix(), expected)
#         self.assertTrue(equal)
#
#     def test_get_stoichiometry_df(self):
#         m = Model()
#         m.add_compounds(['x', 'y'])
#         m.add_reaction('v1', {'x': 1}, 0, 1000)
#         m.add_reaction('v2', {'x': -1, 'y': 1}, 0, 1000)
#         m.add_reaction('v3', {'y': -1}, 0, 1000)
#         self.assertEqual(list(m.get_stoichiometry_df().index), ['x', 'y'])
#         self.assertEqual(list(m.get_stoichiometry_df().columns), ['v1', 'v2', 'v3'])
