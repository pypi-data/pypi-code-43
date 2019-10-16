# flake8: noqa
import unittest
import numpy as np

from modelbase.ode import Model


class TestNumberCompounds(unittest.TestCase):
    def test_number_compounds(self):
        m = Model()
        m.add_compounds(["x", "y"])
        self.assertEqual(m.get_compounds(), {"x": 0, "y": 1})
        self.assertEqual(m.get_all_compounds(), {"x": 0, "y": 1})

    def test_number_compounds_algebraic_module(self):
        m = Model()
        m.add_compounds(["A"])
        m.add_algebraic_module("am1", lambda p: 0, ["A"], ["x", "y"])
        self.assertEqual(m.get_compounds(), {"A": 0})
        self.assertEqual(m.get_all_compounds(), {"A": 0, "x": 1, "y": 2})

    def test_number_compounds_after_am_removal(self):
        m = Model()
        m.add_compounds(["A"])
        m.add_algebraic_module("am1", lambda p: 0, ["A"], ["x", "y"])
        m.remove_algebraic_modules("am1")
        self.assertEqual(m.get_compounds(), {"A": 0})
        self.assertEqual(m.get_all_compounds(), {"A": 0})


class TestRates(unittest.TestCase):
    """Tests for rate creation methods"""

    def test_add_rate_no_variables(self):
        m = Model({"p1": 1})
        m.add_rate("v1", lambda p: p.p1)
        r = m.get_fluxes(0, m.get_full_concentration_dict({}))
        self.assertEqual(r, {"v1": 1})

    def test_add_rate_one_variable(self):
        m = Model({"p1": 1})
        m.add_compounds(["x"])
        m.add_rate("v1", lambda p, x: p.p1 * x, ["x"])
        r = m.get_fluxes(0, m.get_full_concentration_dict([2]))
        self.assertEqual(r, {"v1": 2})

    def test_add_rate_two_variables(self):
        m = Model({"p1": 1})
        m.add_compounds(["x", "y"])
        m.add_rate("v1", lambda p, x, y: p.p1 * x * y, ["x", "y"])
        r = m.get_fluxes(0, m.get_full_concentration_dict([2, 3]))
        self.assertEqual(r, {"v1": 6})

    def test_add_time_dependent_rate_run(self):
        m = Model()
        m.add_compounds("x")
        m.add_reaction("vt", lambda p, t, x: t * x, {"x": -1}, ["time", "x"])
        fcd = m.get_full_concentration_dict([2])
        self.assertEqual(m.get_fluxes(3, fcd), {"vt": 6})

    def test_add_rate_rate_name_type_error_dict(self):
        m = Model({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_rate({"a": 1}, lambda p: p.p1)

    def test_add_rate_rate_name_type_error_set(self):
        m = Model({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_rate({"a"}, lambda p: p.p1)

    def test_add_rate_rate_name_type_error_int(self):
        m = Model({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_rate(1, lambda p: p.p1)

    def test_add_rate_rate_name_type_error_float(self):
        m = Model({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_rate(1.0, lambda p: p.p1)

    def test_add_rate_rate_name_type_error_list(self):
        m = Model({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_rate(["a"], lambda p: p.p1)

    def test_add_rate_rate_function_type_error_dict(self):
        m = Model({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_rate("v1", {"a": 1})

    def test_add_rate_rate_function_type_error_set(self):
        m = Model({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_rate("v1", {"a"})

    def test_add_rate_rate_function_type_error_int(self):
        m = Model({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_rate("v1", 1)

    def test_add_rate_rate_function_type_error_float(self):
        m = Model({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_rate("v1", 1.0)

    def test_add_rate_rate_function_type_error_list(self):
        m = Model({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_rate("v1", ["a"])

    def test_add_rate_variables_type_error_float(self):
        m = Model({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_rate("v1", lambda p: p.v1, 1.0)

    def test_add_rate_variables_type_error_dict(self):
        m = Model({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_rate("v1", lambda p: p.v1, {"a": 1})

    def test_add_rate_variables_type_error_set(self):
        m = Model({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_rate("v1", lambda p: p.v1, {"a"})

    def test_add_rate_variables_type_error_int(self):
        m = Model({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_rate("v1", lambda p: p.v1, 1)

    def test_add_time_dependent_rate(self):
        m = Model()
        m.add_compounds("x")
        m.add_reaction("vt", lambda p, t, x: t * x, {"x": -1}, ["time", "x"])
        # Check if the right compounds are set
        self.assertEqual(m.get_rate_compounds("vt"), ["time", "x"])

    # Remove rates
    def test_remove_rates_one_rate(self):
        m = Model()
        m.add_rate("v1", lambda x: 1)
        m.add_rate("v2", lambda x: 2)
        m.remove_rates("v1")
        self.assertEqual(m.get_rate_names(), ("v2",))

    def test_remove_rates_two_rates(self):
        m = Model()
        m.add_rate("v1", lambda x: 1)
        m.add_rate("v2", lambda x: 2)
        m.remove_rates("v1")
        m.remove_rates("v2")
        self.assertEqual(m.get_rate_names(), ())

    def test_remove_rates_value_error_non_existent_rate(self):
        m = Model()
        with self.assertRaises(ValueError):
            m.remove_rates("v1")

    def test_remove_parameters_type_error_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_rates(1)

    def test_remove_parameters_type_error_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_rates(1.0)

    def test_remove_parameters_type_error_dict(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_rates({"a": 1})

    def test_remove_parameters_type_error_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_rates({"a"})

    # Get rate names
    def test_get_rate_names(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_rate("v1", lambda x: x, ["x"])
        self.assertEqual(m.get_rate_names(), ("v1",))

    # Get rate compounds
    def test_get_rate_compounds(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_rate("v1", lambda x: x, ["x"])
        self.assertEqual(m.get_rate_compounds("v1"), ["x"])

    # Update rates
    def test_update_rates(self):
        m = Model()
        m.add_compounds(["A"])
        m.add_algebraic_module("fast_eq", lambda p, A: (1, 1), ["A"], ["X", "Y"])
        m.add_reaction("v0", lambda p: 1, {"A": 1})
        m.add_reaction("v2", lambda p, A: 1, {"A": -1}, ["Y"])
        self.assertEqual(m.get_rate_compounds(), {"v0": [], "v2": ["Y"]})
        self.assertEqual(m.get_stoichiometries(), {"v0": {"A": 1}, "v2": {"A": -1}})
        m.update_reaction("v0", lambda p, A: 1, {"A": 1}, ["A"])
        self.assertEqual(m.get_rate_compounds(), {"v2": ["Y"], "v0": ["A"]})
        self.assertEqual(m.get_stoichiometries(), {"v2": {"A": -1}, "v0": {"A": 1}})


class StoichiometriesTests(unittest.TestCase):
    """Description"""

    def test_add_one_rate_stoichiometry(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_rate("v1", lambda x: x, ["x"])
        m.add_stoichiometries({"v1": {"x": 1}})
        self.assertEqual(m._stoichiometries, {"v1": {"x": 1}})

    def test_add_multiple_rate_stoichiometries(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_rate("v1", lambda x: x, ["x"])
        m.add_rate("v2", lambda x: x, ["x"])
        m.add_stoichiometries({"v1": {"x": 1}, "v2": {"x": 2}})
        self.assertEqual(m._stoichiometries, {"v1": {"x": 1}, "v2": {"x": 2}})

    def test_add_one_rate_stoichiometry_by_compound(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_rate("v1", lambda x: x, ["x"])
        m.add_stoichiometries_by_compounds({"x": {"v1": 1}})
        self.assertEqual(m._stoichiometries, {"v1": {"x": 1}})

    def test_add_multiple_rate_stoichiometries_by_compound(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_rate("v1", lambda x: x, ["x"])
        m.add_rate("v2", lambda x: x, ["x"])
        m.add_stoichiometries_by_compounds({"x": {"v1": 1, "v2": 2}})
        self.assertEqual(m._stoichiometries, {"v1": {"x": 1}, "v2": {"x": 2}})

    def test_add_stoichiometries_type_error_rate_name_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_stoichiometries(1)

    def test_add_stoichiometries_type_error_rate_name_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_stoichiometries(1.0)

    def test_add_stoichiometries_type_error_rate_name_str(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_stoichiometries("a")

    def test_add_stoichiometries_type_error_rate_name_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_stoichiometries({"a"})

    def test_add_stoichiometries_type_error_rate_name_list(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_stoichiometries(["a"])

    def test_add_stoichiometries_type_error_stoichiometries_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_stoichiometries({"v1": 1})

    def test_add_stoichiometries_type_error_stoichiometries_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_stoichiometries({"v1": 1.0})

    def test_add_stoichiometries_type_error_stoichiometries_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_stoichiometries({"v1": {"a"}})

    def test_add_stoichiometries_type_error_stoichiometries_list(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_stoichiometries({"v1": ["a"]})

    # Remove stoichiometry
    def test_remove_one_rate_stoichiometry(self):
        m = Model()
        m.add_stoichiometries_by_compounds({"x": {"v1": 1, "v2": 2}})
        m.remove_stoichiometries("v1")
        self.assertEqual(m._stoichiometries, {"v2": {"x": 2}})

    def test_remove_two_rate_stoichiometries(self):
        m = Model()
        m.add_stoichiometries_by_compounds({"x": {"v1": 1, "v2": 2, "v3": 3}})
        m.remove_stoichiometries(["v1", "v2"])
        self.assertEqual(m._stoichiometries, {"v3": {"x": 3}})

    def test_remove_stoichiometries_value_error_non_existent(self):
        m = Model()
        with self.assertRaises(ValueError):
            m.remove_stoichiometries("v1")

    def test_remove_stoichiometries_type_error_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_stoichiometries(1)

    def test_remove_stoichiometries_type_error_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_stoichiometries(1.0)

    def test_remove_stoichiometries_type_error_dict(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_stoichiometries({"a": 1})

    def test_remove_stoichiometries_type_error_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_stoichiometries({"a"})

    # Get functions
    def test_get_stoichiometries(self):
        m = Model()
        m.add_stoichiometries({"v1": {"x": 1}})
        self.assertEqual(m.get_stoichiometries(), {"v1": {"x": 1}})

    def test_get_stoichiometries_by_compounds(self):
        m = Model()
        m.add_stoichiometries({"v1": {"x": 1}})
        self.assertEqual(m.get_stoichiometries(by="Compounds"), {"x": {"v1": 1}})

    # Stoichiometric matrix
    def test_get_stoichiometric_matrix(self):
        m = Model()
        m.add_compounds(["x", "y"])
        m.add_rate("v1", lambda p, x: 1, ["x"])
        m.add_rate("v2", lambda p, x: 1, ["y"])
        m.add_stoichiometries({"v1": {"x": 1, "y": -1}})
        m.add_stoichiometries({"v2": {"x": -1, "y": 1}})
        self.assertEqual(
            np.sum(m.get_stoichiometry_matrix() - np.array([[1.0, -1.0], [-1.0, 1.0]])),
            0,
        )

    def test_get_stoichiometric_data_frame(self):
        m = Model()
        m.add_compounds(["x", "y"])
        m.add_rate("v1", lambda p, x: 1, ["x"])
        m.add_rate("v2", lambda p, x: 1, ["y"])
        m.add_stoichiometries({"v1": {"x": 1, "y": -1}})
        m.add_stoichiometries({"v2": {"x": -1, "y": 1}})
        self.assertEqual(
            np.sum(
                m.get_stoichiometry_df().values - np.array([[1.0, -1.0], [-1.0, 1.0]])
            ),
            0,
        )


class ReactionsTests(unittest.TestCase):
    """Tests for rate creation methods"""

    def test_add_reaction_one_reaction(self):
        m = Model()
        m.add_compounds(["x", "y"])
        m.add_reaction("v1", lambda p, x: x, {"x": 1}, ["x"])
        self.assertEqual(m.get_rate_names(), ("v1",))
        self.assertEqual(m.get_stoichiometries(), {"v1": {"x": 1}})

    def test_add_reaction_two_reactions(self):
        m = Model()
        m.add_compounds(["x", "y"])
        m.add_reaction("v1", lambda p, x: x, {"x": 1}, ["x"])
        m.add_reaction("v2", lambda p, y: y, {"y": 2}, ["y"])
        self.assertEqual(m.get_rate_names(), ("v1", "v2"))
        self.assertEqual(m.get_stoichiometries(), {"v1": {"x": 1}, "v2": {"y": 2}})

    def test_add_reaction_type_error_rate_name_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction(1, lambda p, x: x, {"x": 1}, ["x"])

    def test_add_reaction_type_error_rate_name_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction(1.0, lambda p, x: x, {"x": 1}, ["x"])

    def test_add_reaction_type_error_rate_name_list(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction(["a"], lambda p, x: x, {"x": 1}, ["x"])

    def test_add_reaction_type_error_rate_name_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction({"a"}, lambda p, x: x, {"x": 1}, ["x"])

    def test_add_reaction_type_error_rate_name_dict(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction({"a": 1}, lambda p, x: x, {"x": 1}, ["x"])

    def test_add_reaction_type_error_rate_function_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", 1, {"x": 1}, ["x"])

    def test_add_reaction_type_error_rate_function_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", 1.0, {"x": 1}, ["x"])

    def test_add_reaction_type_error_rate_function_list(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", ["a"], {"x": 1}, ["x"])

    def test_add_reaction_type_error_rate_function_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", {"a"}, {"x": 1}, ["x"])

    def test_add_reaction_type_error_rate_function_dict(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", {"a": 1}, {"x": 1}, ["x"])

    def test_add_reaction_type_error_rate_function_str(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", "a", {"x": 1}, ["x"])

    def test_add_reaction_type_error_stoichiometries_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", lambda p, x: x, 1, ["x"])

    def test_add_reaction_type_error_stoichiometries_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", lambda p, x: x, 1.0, ["x"])

    def test_add_reaction_type_error_stoichiometries_list(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", lambda p, x: x, ["a"], ["x"])

    def test_add_reaction_type_error_stoichiometries_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", lambda p, x: x, {"a"}, ["x"])

    def test_add_reaction_type_error_stoichiometries_str(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", lambda p, x: x, {"a"}, ["x"])

    def test_add_reaction_type_error_variables_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", lambda p, x: x, {"x": 1}, 1)

    def test_add_reaction_type_error_variables_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", lambda p, x: x, {"x": 1}, 1.0)

    def test_add_reaction_type_error_variables_dict(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", lambda p, x: x, {"x": 1}, {"a": 1})

    def test_add_reaction_type_error_variables_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", lambda p, x: x, {"x": 1}, {"a"})

    def test_add_reaction_type_error_variables_str(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_reaction("v1", lambda p, x: x, {"x": 1}, "a")

    # Remove reactions
    def test_remove_one_reaction(self):
        m = Model()
        m.add_compounds(["x", "y"])
        m.add_reaction("v1", lambda p, x: x, {"x": 1}, ["x"])
        m.add_reaction("v2", lambda p, y: y, {"y": 2}, ["y"])
        m.remove_reactions("v1")
        self.assertEqual(m.get_rate_names(), ("v2",))
        self.assertEqual(m.get_stoichiometries(), {"v2": {"y": 2}})

    def test_remove_two_reactions(self):
        m = Model()
        m.add_compounds(["x", "y", "z"])
        m.add_reaction("v1", lambda p, x: x, {"x": 1}, ["x"])
        m.add_reaction("v2", lambda p, y: y, {"y": 2}, ["y"])
        m.add_reaction("v3", lambda p, z: z, {"z": 3}, ["z"])
        m.remove_reactions(["v1", "v3"])
        self.assertEqual(m.get_rate_names(), ("v2",))
        self.assertEqual(m.get_stoichiometries(), {"v2": {"y": 2}})

    def test_remove_reaction_value_error_non_existent(self):
        m = Model()
        with self.assertRaises(ValueError):
            m.remove_rates("v1")

    def test_remove_reactions_type_error_dict(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_rates({"a": 1})

    def test_remove_reactions_type_error_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_rates(1)

    def test_remove_reactions_type_error_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_rates(1.0)

    def test_remove_reactions_type_error_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_rates({"a"})


class AlgebraicModuleTests(unittest.TestCase):
    """Description"""

    def test_add_algebraic_module(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_algebraic_module("am", lambda p, x: x, ["x"], ["A"])
        self.assertEqual(m._all_compounds, {"x": 0, "A": 1})

    def test_add_algebraic_module_two_derived_vars(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_algebraic_module("am", lambda p, x: x, ["x"], ["A", "B"])
        self.assertEqual(m._all_compounds, {"x": 0, "A": 1, "B": 2})

    def test_add_algebraic_module_two_modules(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_algebraic_module("am", lambda p, x: x, ["x"], ["A", "B"])
        m.add_algebraic_module("am2", lambda p, x: x, ["x"], ["C"])
        self.assertEqual(m._all_compounds, {"x": 0, "A": 1, "B": 2, "C": 3})

    def test_add_algebraic_module_two_vars_two_modules(self):
        m = Model()
        m.add_compounds(["x", "y"])
        m.add_algebraic_module("am", lambda p, x: x, ["x"], ["A"])
        m.add_algebraic_module("am2", lambda p, x: x, ["x", "y"], ["B"])
        self.assertEqual(m._all_compounds, {"x": 0, "y": 1, "A": 2, "B": 3})

    def test_add_algebraic_module_type_error_module_name_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module(1, lambda p, x: x, ["x"], ["A"])

    def test_add_algebraic_module_type_error_module_name_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module(1.0, lambda p, x: x, ["x"], ["A"])

    def test_add_algebraic_module_type_error_module_name_list(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module(["a"], lambda p, x: x, ["x"], ["A"])

    def test_add_algebraic_module_type_error_module_name_dict(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module({"a": 1}, lambda p, x: x, ["x"], ["A"])

    def test_add_algebraic_module_type_error_module_name_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module({"a"}, lambda p, x: x, ["x"], ["A"])

    def test_add_algebraic_module_type_error_function_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", 1, ["x"], ["A"])

    def test_add_algebraic_module_type_error_function_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", 1.0, ["x"], ["A"])

    def test_add_algebraic_module_type_error_function_str(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", "a", ["x"], ["A"])

    def test_add_algebraic_module_type_error_function_list(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", ["a"], ["x"], ["A"])

    def test_add_algebraic_module_type_error_function_dict(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", {"a": 1}, ["x"], ["A"])

    def test_add_algebraic_module_type_error_function_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", {"a"}, ["x"], ["A"])

    def test_add_algebraic_module_type_error_vars_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", lambda p, x: x, 1, ["A"])

    def test_add_algebraic_module_type_error_vars_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", lambda p, x: x, 1.0, ["A"])

    def test_add_algebraic_module_type_error_vars_str(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", lambda p, x: x, "a", ["A"])

    def test_add_algebraic_module_type_error_vars_dict(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", lambda p, x: x, {"a": 1}, ["A"])

    def test_add_algebraic_module_type_error_vars_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", lambda p, x: x, {"a"}, ["A"])

    def test_add_algebraic_module_type_error_der_vars_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", lambda p, x: x, ["x"], 1)

    def test_add_algebraic_module_type_error_der_vars_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", lambda p, x: x, ["x"], 1.0)

    def test_add_algebraic_module_type_error_der_vars_str(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", lambda p, x: x, ["x"], "a")

    def test_add_algebraic_module_type_error_der_vars_dict(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", lambda p, x: x, ["x"], {"a": 1})

    def test_add_algebraic_module_type_error_der_vars_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_algebraic_module("am", lambda p, x: x, ["x"], {"a"})

    # Remove algebraic modules
    def test_remove_algebraic_modules_one_module(self):
        m = Model()
        m.add_compounds(["x", "y"])
        m.add_algebraic_module("am", lambda p, x: x, ["x"], ["A"])
        m.add_algebraic_module("am2", lambda p, x: x, ["x", "y"], ["B"])
        m.remove_algebraic_modules("am")
        self.assertTrue(m._all_compounds, {"x": 0, "y": 1, "B": 2})

    def test_remove_algebraic_modules_two_modules(self):
        m = Model()
        m.add_compounds(["x", "y"])
        m.add_algebraic_module("am", lambda p, x: x, ["x"], ["A"])
        m.add_algebraic_module("am2", lambda p, x: x, ["x", "y"], ["B"])
        m.add_algebraic_module("am3", lambda p, x: x, ["y"], ["C"])
        m.remove_algebraic_modules(["am", "am3"])
        self.assertTrue(m._all_compounds, {"x": 0, "y": 1, "B": 2})

    def test_remove_algebraic_modules_value_error_non_existent(self):
        m = Model()
        with self.assertRaises(ValueError):
            m.remove_algebraic_modules("am")

    def test_remove_algebraic_modules_type_error_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_algebraic_modules(1)

    def test_remove_algebraic_modules_type_error_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_algebraic_modules(1.0)

    def test_remove_algebraic_modules_type_error_dict(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_algebraic_modules({"a": 1})

    def test_remove_algebraic_modules_type_error_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_algebraic_modules({"a"})

    # Get algebraic module compounds
    def test_get_algebraic_module_compounds(self):
        m = Model()
        m.add_compounds(["x", "y"])
        m.add_algebraic_module("am", lambda p, x: x, ["x"], ["A"])
        self.assertEqual(m.get_algebraic_module_compounds("am"), ["x"])

    def test_get_algebraic_module_derived_compounds(self):
        m = Model()
        m.add_compounds(["x", "y"])
        m.add_algebraic_module("am", lambda p, x: x, ["x"], ["A"])
        self.assertEqual(m.get_algebraic_module_derived_compounds("am"), ["A"])


class MiscTests(unittest.TestCase):
    """Description"""

    def test_check_for_compounds_without_reactions_empty(self):
        m = Model()
        m.add_compounds(["A"])
        m.add_reaction("v0", lambda p: 1, {"A": 1})
        self.assertEqual(m.check_for_compounds_without_reactions(), [])

    def test_check_for_compounds_without_reactions(self):
        m = Model()
        m.add_compounds(["A", "B"])
        m.add_reaction("v0", lambda p: 1, {"A": 1})
        self.assertEqual(m.check_for_compounds_without_reactions(), ["B"])


if __name__ == "__main__":
    unittest.main()
