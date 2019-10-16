import unittest
import numpy as np
from modelbase.ode import LabelModel


class TestLabelModel(unittest.TestCase):
    def test_generate_y0(self):
        m = LabelModel()
        m.add_carbon_compounds({"x": 2, "y": 2, "ATP": 0})
        self.assertTrue(
            np.array_equal(
                m._generate_y0({"x": 1, "y": 1, "ATP": 2}, None),
                [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 2.0],
            )
        )

        self.assertTrue(
            np.array_equal(
                m._generate_y0({"x": 0, "y": 1, "ATP": 2}, None),
                [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 2.0],
            )
        )

        self.assertTrue(
            np.array_equal(
                m._generate_y0({"x": 1, "y": 0, "ATP": 2}, None),
                [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0],
            )
        )

    def test_generate_y0_position_one(self):
        m = LabelModel()
        m.add_carbon_compounds({"x": 2, "y": 2, "ATP": 0})
        expected = [0.0, 0.0, 1.0, 0.0, 2.0, 0.0, 0.0, 0.0, 3.0]
        result = m._generate_y0({"x": 1, "y": 2, "ATP": 3}, {"x": 0})
        self.assertTrue(np.array_equal(expected, result))

    def test_generate_y0_position_two(self):
        m = LabelModel()
        m.add_carbon_compounds({"x": 2, "y": 2, "ATP": 0})
        expected = [0.0, 1.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 3.0]
        result = m._generate_y0({"x": 1, "y": 2, "ATP": 3}, {"x": 1})
        self.assertTrue(np.array_equal(expected, result))

    def test_generate_y0_position_one_and_two(self):
        m = LabelModel()
        m.add_carbon_compounds({"x": 2, "y": 2, "ATP": 0})
        expected = [0.0, 0.0, 0.0, 1.0, 2.0, 0.0, 0.0, 0.0, 3.0]
        result = m._generate_y0({"x": 1, "y": 2, "ATP": 3}, {"x": [0, 1]})
        self.assertTrue(np.array_equal(expected, result))

    def test_generate_y0_position_two_compounds(self):
        m = LabelModel()
        m.add_carbon_compounds({"x": 2, "y": 2, "ATP": 0})
        expected = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 2.0, 0.0, 3.0]
        result = m._generate_y0({"x": 1, "y": 2, "ATP": 3}, {"x": [0, 1], "y": 0})
        self.assertTrue(np.array_equal(expected, result))

    def test_add_carbon_compounds(self):
        expected = {
            "x_00": 0,
            "x_01": 1,
            "x_10": 2,
            "x_11": 3,
            "y_00": 4,
            "y_01": 5,
            "y_10": 6,
            "y_11": 7,
        }

        m = LabelModel()
        m.add_carbon_compounds({"x": 2, "y": 2})
        self.assertEqual(m.get_compounds(), expected)

    def test_add_non_carbon_compounds(self):
        m = LabelModel()
        m.add_carbon_compounds("ATP", 0)
        self.assertEqual(m.get_compounds(), {"ATP": 0})

    def test_add_carbonmap_reaction_without_carbons(self):
        expected = {"v1": {"X": -1, "Y": 1}}
        m = LabelModel()
        m.add_carbon_compounds({"X": 0, "Y": 0})
        m.add_carbonmap_reaction("v1", lambda p, *args: 1, [], ["X"], ["Y"])
        self.assertEqual(m.get_stoichiometries(), expected)

    def test_add_carbonmap_reaction(self):
        expected = {
            "v1_00": {"x_00": -1, "y_00": 1},
            "v1_01": {"x_01": -1, "y_01": 1},
            "v1_10": {"x_10": -1, "y_10": 1},
            "v1_11": {"x_11": -1, "y_11": 1},
        }
        m = LabelModel()
        m.add_carbon_compounds({"x": 2, "y": 2})
        m.add_carbonmap_reaction("v1", lambda p, x: 1, [0, 1], ["x"], ["y"])
        self.assertEqual(m.get_stoichiometries(), expected)

    def test_add_carbonmap_reaction_shifted(self):
        expected = {
            "v1_00": {"x_00": -1, "y_00": 1},
            "v1_01": {"x_01": -1, "y_10": 1},
            "v1_10": {"x_10": -1, "y_01": 1},
            "v1_11": {"x_11": -1, "y_11": 1},
        }
        m = LabelModel()
        m.add_carbon_compounds({"x": 2, "y": 2})
        m.add_carbonmap_reaction("v1", lambda p, x: 1, [1, 0], ["x"], ["y"])
        self.assertEqual(m.get_stoichiometries(), expected)

    def test_add_carbonmap_reaction_cofactor_rate_arguments(self):
        m = LabelModel()
        m.add_carbon_compounds({"x": 2, "y": 2, "ATP": 0, "z": 0})
        m.add_carbonmap_reaction(
            "v1", lambda p, x, ATP, z: x / (ATP * z), [0, 1], ["x", "ATP"], ["y"], ["z"]
        )

        self.assertEqual(m.get_rate_compounds("v1_00"), ["x_00", "ATP", "z"])

    def test_add_carbonmap_reaction_additional_arguments(self):
        # All x are 1, all y 0. ATP is 5, z is 10. Should therefore yield 0.02
        expected = {"v1_00": 0.02, "v1_01": 0.02, "v1_10": 0.02, "v1_11": 0.02}
        m = LabelModel()
        m.add_carbon_compounds({"x": 2, "y": 2, "ATP": 0, "z": 0})
        m.add_carbonmap_reaction(
            "v1", lambda p, x, ATP, z: x / (ATP * z), [0, 1], ["x", "ATP"], ["y"], ["z"]
        )
        fcd = m.get_full_concentration_dict([1, 1, 1, 1, 0, 0, 0, 0, 5, 10])
        self.assertEqual(m.get_fluxes(0, fcd), expected)

    def test_add_carbonmap_reaction_cofactor(self):
        expected = {
            "v1_00": {"x_00": -1, "ATP": -1, "y_00": 1},
            "v1_01": {"x_01": -1, "ATP": -1, "y_01": 1},
            "v1_10": {"x_10": -1, "ATP": -1, "y_10": 1},
            "v1_11": {"x_11": -1, "ATP": -1, "y_11": 1},
        }
        m = LabelModel()
        m.add_carbon_compounds({"x": 2, "y": 2, "ATP": 0})
        m.add_carbonmap_reaction("v1", lambda p, x, ATP: 1, [0, 1], ["x", "ATP"], ["y"])
        self.assertEqual(m.get_stoichiometries(), expected)

    def test_add_carbonmap_reaction_cofactor_argument_order(self):
        expected = {
            "v1_00": {"ATP": -1, "x_00": -1, "y_00": 1},
            "v1_01": {"ATP": -1, "x_01": -1, "y_01": 1},
            "v1_10": {"ATP": -1, "x_10": -1, "y_10": 1},
            "v1_11": {"ATP": -1, "x_11": -1, "y_11": 1},
        }
        m = LabelModel()
        m.add_carbon_compounds({"x": 2, "y": 2, "ATP": 0})
        m.add_carbonmap_reaction("v1", lambda p, x, ATP: 1, [0, 1], ["x", "ATP"], ["y"])
        self.assertEqual(m.get_stoichiometries(), expected)

    def test_add_carbonmap_external_labels_none(self):
        m = LabelModel()
        m.add_carbon_compounds({"x": 1, "y": 2})
        m.add_carbonmap_reaction("v1", lambda p, *args: 0, [0, 1], ["x"], ["y"])

        expected = {"v1_0": {"x_0": -1, "y_01": 1}, "v1_1": {"x_1": -1, "y_11": 1}}
        result = m.get_stoichiometries()
        self.assertEqual(result, expected)

    def test_add_carbonmap_external_labels_empty_list(self):
        m = LabelModel()
        m.add_carbon_compounds({"x": 1, "y": 2})
        m.add_carbonmap_reaction(
            "v1", lambda p, *args: 0, [0, 1], ["x"], ["y"], external_labels=[]
        )

        expected = {"v1_0": {"x_0": -1, "y_00": 1}, "v1_1": {"x_1": -1, "y_10": 1}}
        result = m.get_stoichiometries()
        self.assertEqual(result, expected)

    def test_add_carbonmap_external_labels_specified(self):
        m = LabelModel()
        m.add_carbon_compounds({"x": 1, "y": 2})
        m.add_carbonmap_reaction(
            "v1", lambda p, *args: 0, [0, 1], ["x"], ["y"], external_labels=[0]
        )

        expected = {"v1_0": {"x_0": -1, "y_01": 1}, "v1_1": {"x_1": -1, "y_11": 1}}
        result = m.get_stoichiometries()
        self.assertEqual(result, expected)

    def test_get_full_concentration_dict(self):
        expected = {
            "x_00": 1,
            "x_01": 1,
            "x_10": 1,
            "x_11": 1,
            "y_00": 2,
            "y_01": 2,
            "y_10": 2,
            "y_11": 2,
            "ATP": 3,
            "x_total": 4,
            "y_total": 8,
        }
        m = LabelModel()
        m.add_carbon_compounds({"x": 2, "y": 2, "ATP": 0})
        m.add_carbonmap_reaction(
            "v1", lambda p, x, ATP: x * ATP, [0, 1], ["ATP", "x"], ["y"]
        )
        self.assertEqual(
            m.get_full_concentration_dict([1, 1, 1, 1, 2, 2, 2, 2, 3]), expected
        )

    def test_get_fluxes(self):
        m = LabelModel()
        m.add_carbon_compounds({"x": 2, "y": 2, "ATP": 0})
        m.add_carbonmap_reaction(
            "v1", lambda p, x, ATP: x * ATP, [0, 1], ["ATP", "x"], ["y"]
        )
        fcd = m.get_full_concentration_dict([1, 1, 1, 1, 0, 0, 0, 0, 3])
        self.assertEqual(
            m.get_fluxes(0, fcd), {"v1_00": 3, "v1_01": 3, "v1_10": 3, "v1_11": 3}
        )

    def test_total_compound_algebraic_module(self):
        expected = {"x_00": 1, "x_01": 1, "x_10": 1, "x_11": 1, "x_total": 4}
        m = LabelModel()
        m.add_carbon_compounds({"x": 2})
        self.assertEqual(m.get_full_concentration_dict([1, 1, 1, 1]), expected)


class TestLabelScope(unittest.TestCase):
    def test_get_label_scope(self):
        m = LabelModel()
        m.add_carbon_compounds({"a": 2, "b": 2, "c": 2, "d": 2})
        m.add_carbonmap_reaction("v1", lambda p, x: x, [0, 1], ["a"], ["b"])
        m.add_carbonmap_reaction("v2", lambda p, x: x, [0, 1], ["b"], ["c"])
        m.add_carbonmap_reaction("v3", lambda p, x: x, [0, 1], ["c"], ["d"])
        m.add_carbonmap_reaction("v4", lambda p, x: x, [1, 0], ["d"], ["a"])

        expected = {
            0: {"b_01"},
            1: {"c_01"},
            2: {"d_01"},
            3: {"a_10"},
            4: {"b_10"},
            5: {"c_10"},
            6: {"d_10"},
        }
        self.assertEqual(expected, m.get_label_scope(["a_01"]))


if __name__ == "__main__":
    unittest.main()
