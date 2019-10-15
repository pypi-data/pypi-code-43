# flake8: noqa

import unittest
from modelbase.core import Model, ParameterModel


class CompoundModelTests(unittest.TestCase):
    """Tests for compound methods"""

    # Add compounds
    def test_add_compounds_str(self):
        m = Model()
        m.add_compounds("x")
        self.assertEqual(m._compounds, {"x": 0})

    def test_add_compounds_list(self):
        m = Model()
        m.add_compounds(["x", "y"])
        self.assertEqual(m._compounds, {"x": 0, "y": 1})

    def test_add_compounds_type_error_dict(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_compounds(dict())

    def test_add_compounds_type_error_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_compounds(set())

    def test_add_compounds_type_error_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_compounds(int())

    def test_add_compounds_type_error_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_compounds(float())

    def test_add_compounds_type_error_none(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.add_compounds(None)

    # Remove compounds
    def test_remove_compounds_str(self):
        m = Model()
        m.add_compounds(["x", "y"])
        m.remove_compounds("x")
        self.assertEqual(m._compounds, {"y": 0})

    def test_remove_compounds_list(self):
        m = Model()
        m.add_compounds(["x", "y", "z"])
        m.remove_compounds(["x", "z"])
        self.assertEqual(m._compounds, {"y": 0})

    def test_remove_compounds_type_error_dict(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_compounds(dict())

    def test_remove_compounds_type_error_set(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_compounds(set())

    def test_remove_compounds_type_error_int(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_compounds(int())

    def test_remove_compounds_type_error_float(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_compounds(float())

    def test_remove_compounds_type_error_none(self):
        m = Model()
        with self.assertRaises(TypeError):
            m.remove_compounds(None)

    # Get compounds
    def test_get_compounds(self):
        m = Model()
        m.add_compounds(["x", "y", "z"])
        self.assertEqual(m._compounds, m.get_compounds())

    # Number compounds
    def test_number_compounds(self):
        m = Model()
        m.add_compounds(["x", "y", "z"])
        self.assertEqual(m._compounds, {"x": 0, "y": 1, "z": 2})

    def test_number_compounds_after_removal(self):
        m = Model()
        m.add_compounds(["x", "y", "z"])
        m.remove_compounds("y")
        self.assertEqual(m._compounds, {"x": 0, "z": 1})


class StoichiometryTests(unittest.TestCase):
    def test_add_stoichiometry(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_stoichiometry("v1", {"x": 1})
        self.assertEqual(m._stoichiometries, {"v1": {"x": 1}})

    def test_add_stoichiometries(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_stoichiometries({"v1": {"x": -1}, "v2": {"x": 1}})
        self.assertEqual(m._stoichiometries, {"v1": {"x": -1}, "v2": {"x": 1}})

    def test_add_stoichiometry_by_compound(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_stoichiometry_by_compound("x", {"v1": 1})
        self.assertEqual(m._stoichiometries, {"v1": {"x": 1}})

    def test_add_stoichiometries_by_compounds(self):
        m = Model()
        m.add_compounds(["x", "y"])
        m.add_stoichiometries_by_compounds({"x": {"v1": -1}, "y": {"v1": 1}})
        self.assertEqual(m._stoichiometries, {"v1": {"x": -1, "y": 1}})

    def test_remove_stoichiometry(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_stoichiometries({"v1": {"x": -1}, "v2": {"x": 1}})
        m.remove_stoichiometries("v2")
        self.assertEqual(m._stoichiometries, {"v1": {"x": -1}})

    def test_remove_stoichiometries(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_stoichiometries({"v1": {"x": -1}, "v2": {"x": 1}, "v3": {"x": 1}})
        m.remove_stoichiometries(["v2", "v3"])
        self.assertEqual(m._stoichiometries, {"v1": {"x": -1}})

    def test_get_stoichiometries(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_stoichiometries({"v1": {"x": -1}, "v2": {"x": 1}})
        self.assertEqual(m.get_stoichiometries(), {"v1": {"x": -1}, "v2": {"x": 1}})

    def test_get_stoichiometries_by_compounds(self):
        m = Model()
        m.add_compounds(["x"])
        m.add_stoichiometries({"v1": {"x": -1}, "v2": {"x": 1}})
        self.assertEqual(m.get_stoichiometries("Compounds"), {"x": {"v1": -1, "v2": 1}})


class ParameterModelTests(unittest.TestCase):
    def test_add_parameters(self):
        m = ParameterModel()
        m.add_parameters({"p1": 1})
        self.assertEqual(m.get_all_parameters(), {"p1": 1})

    def test_add_duplicate_parameter(self):
        m = ParameterModel()
        m.add_parameters({"p1": 1})
        with self.assertRaises(ValueError):
            m.add_parameters({"p1": 2})

    def test_update_parameters(self):
        m = ParameterModel()
        m.add_parameters({"p1": 1})
        m.update_parameters({"p1": 2})
        self.assertEqual(m.get_all_parameters(), {"p1": 2})

    def test_update_nonexistent_parameter(self):
        m = ParameterModel()
        with self.assertRaises(ValueError):
            m.update_parameters({"p1": 2})

    def test_add_and_update_parameters(self):
        m = ParameterModel()
        m.add_parameters({"p1": 1})
        m.add_and_update_parameters({"p1": 2, "p2": 2})
        self.assertEqual(m.get_all_parameters(), {"p1": 2, "p2": 2})

    def test_remove_parameter(self):
        m = ParameterModel()
        m.add_parameters({"p1": 1, "p2": 2})
        m.remove_parameters("p1")
        self.assertEqual(m.get_all_parameters(), {"p2": 2})

    def test_remove_parameters(self):
        m = ParameterModel()
        m.add_parameters({"p1": 1, "p2": 2, "p3": 3})
        m.remove_parameters(["p1", "p3"])
        self.assertEqual(m.get_all_parameters(), {"p2": 2})

    def test_get_parameter(self):
        m = ParameterModel()
        m.add_parameters({"p1": 1})
        self.assertEqual(m.get_parameter("p1"), 1)


class ContextManagerTests(unittest.TestCase):
    def test_direct_copy(self):
        m = ParameterModel({"k0": 1})
        with m:
            m.update_parameters({"k0": 2})
            self.assertEqual(m.get_parameter("k0"), 2)

    def test_direct_copy_revert_change(self):
        m = ParameterModel({"k0": 1})
        with m:
            m.update_parameters({"k0": 2})
        self.assertEqual(m.get_parameter("k0"), 1)

    def test_returned_copy(self):
        m = ParameterModel({"k0": 1})
        with m as temp:
            temp.update_parameters({"k0": 2})
            self.assertEqual(temp.get_parameter("k0"), 2)

    def test_returned_copy_revert_change(self):
        m = ParameterModel({"k0": 1})
        with m as temp:
            temp.update_parameters({"k0": 2})
        self.assertEqual(m.get_parameter("k0"), 1)


if __name__ == "__main__":
    unittest.main()
