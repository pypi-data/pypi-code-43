# import unittest
# import numpy as np
# from modelbase.stoichiometric import Model, Simulator


# class TestStoichiometricSimulator(unittest.TestCase):
#     model = Model()
#     model.add_compounds(['x', 'y'])
#     model.add_reaction('v1', {'x': 1}, 0, 1000)
#     model.add_reaction('v2', {'x': -1, 'y': 1}, 0, 1000)
#     model.add_reaction('v3', {'y': -1}, 0, 1000)
#
#     def test_set_objective_function(self):
#         s = Simulator(self.__class__.model)
#         s.set_objective_function({'v1': 1})
#         self.assertTrue(s._cobra_model.objective.expression,
#                         '1.0*v1 - 1.0*v1_reverse_6654c')
#
#     def test_simulation(self):
#         s = Simulator(self.__class__.model)
#         s.set_objective_function({'v1': 1})
#         expected = [[1000.0, 0.0], [1000.0, 0.0], [1000.0, 2.0]]
#         equal = np.array_equal(s.simulate().to_frame().values, expected)
#         self.assertTrue(equal)
#
#     def test_get_solution_status(self):
#         s = Simulator(self.__class__.model)
#         s.set_objective_function({'v1': 1})
#         s.simulate()
#         self.assertEqual(s.get_solution_status(), 'optimal')
#
#     def test_get_objective_value(self):
#         s = Simulator(self.__class__.model)
#         s.set_objective_function({'v1': 1})
#         s.simulate()
#         self.assertEqual(s.get_objective_value(), 1000.0)
#
#     def test_get_solution_fluxes(self):
#         s = Simulator(self.__class__.model)
#         s.set_objective_function({'v1': 1})
#         s.simulate()
#         equal = np.array_equal(s.get_solution_fluxes().values, [1000., 1000., 1000.])
#         self.assertTrue(equal)
#
#     def test_get_solution_shadow_prices(self):
#         s = Simulator(self.__class__.model)
#         s.set_objective_function({'v1': 1})
#         s.simulate()
#         equal = np.array_equal(s.get_solution_shadow_prices().values, [1., 1.])
#         self.assertTrue(equal)
