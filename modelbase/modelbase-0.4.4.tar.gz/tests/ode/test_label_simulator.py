# flake8: noqa
import unittest
import numpy as np
from modelbase.ode import LabelModel, Simulator


class TestLabelSimulator(unittest.TestCase):
    def test_set_initial_conditions(self):
        m = LabelModel()
        m.add_carbon_compounds({"x": 2})
        s = Simulator(m)
        s.set_initial_conditions({"x": 2})
        # x_00
        self.assertTrue(np.array_equal(s._y0, np.array([2.0, 0.0, 0.0, 0.0])))

    def test_set_initial_conditions_pos_one(self):
        m = LabelModel()
        m.add_carbon_compounds({"x": 2})
        s = Simulator(m)
        s.set_initial_conditions({"x": 2}, label_position={"x": 0})
        # x_10
        self.assertTrue(np.array_equal(s._y0, np.array([0.0, 0.0, 2.0, 0.0])))

    def test_set_initial_conditions_pos_two(self):
        m = LabelModel()
        m.add_carbon_compounds({"x": 2})
        s = Simulator(m)
        s.set_initial_conditions({"x": 2}, label_position={"x": 1})
        # x_01
        self.assertTrue(np.array_equal(s._y0, np.array([0.0, 2.0, 0.0, 0.0])))

    def test_set_initial_conditions_pos_one_and_two(self):
        m = LabelModel()
        m.add_carbon_compounds({"x": 2})
        s = Simulator(m)
        s.set_initial_conditions({"x": 2}, label_position={"x": [0, 1]})
        # x_11
        self.assertTrue(np.array_equal(s._y0, np.array([0.0, 0.0, 0.0, 2.0])))


class TestAllFunctionsWithToyModel(unittest.TestCase):
    """Uses a toy model, that is in steady state regarding both labels and compounds"""

    m = LabelModel()
    m.add_carbon_compounds({"x": 2, "y": 2})
    m.add_reaction("v_in", lambda p: 1, {"x_10": 1})
    m.add_carbonmap_reaction("v_xy", lambda p, x: x, [1, 0], ["x"], ["y"])
    m.add_carbonmap_reaction("v_out", lambda p, y: y, [0, 1], ["y"], [])
    s = Simulator(m)
    s.set_initial_conditions({"x": 1, "y": 1}, label_position={"x": 0, "y": 1})
    t, y = s.simulate(5, 5)

    def test_get_time(self):
        self.assertTrue(
            np.array_equal(self.__class__.s.get_time(), [0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
        )

    def test_get_y(self):
        expected = np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            ]
        )
        self.assertTrue(np.array_equal(self.__class__.s.get_y(), expected))

    def test_get_results(self):
        t_expected = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
        y_expected = np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            ]
        )

        t, y = self.__class__.s.get_results()
        self.assertTrue(np.array_equal(t, t_expected))
        self.assertTrue(np.array_equal(y, y_expected))

    def test_get_results_dict(self):
        expected = {
            "time": np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0]),
            "x_00": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            "x_01": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            "x_10": np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
            "x_11": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            "y_00": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            "y_01": np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
            "y_10": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            "y_11": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            "x_total": np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
            "y_total": np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
        }
        result = self.__class__.s.get_results_dict()
        for key, array in expected.items():
            self.assertTrue(np.array_equal(result[key], array))

    def test_get_results_df(self):
        df = self.__class__.s.get_results_df()
        self.assertTrue(
            np.array_equal(df["x_total"].values, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
        )

    def test_get_total_concentration(self):
        expected = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        result = self.__class__.s.get_total_concentration("x")
        self.assertTrue(np.array_equal(expected, result))

    def test_get_total_label_concentration(self):
        expected = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        result = self.__class__.s.get_total_label_concentration("x")
        self.assertTrue(np.array_equal(expected, result))

    def test_get_all_compound_variants(self):
        expected = {
            "x_00": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            "x_01": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            "x_10": np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
            "x_11": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        }
        result = self.__class__.s.get_all_compound_variants("x")
        for key, array in expected.items():
            self.assertTrue(np.array_equal(result[key], array))

    def test_get_compounds_by_reg_exp(self):
        expected = [
            np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
            np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        ]
        result = self.__class__.s.get_compounds_by_reg_exp("x_[01][01]")
        self.assertTrue(np.array_equal(expected, result))

    def test_get_compound_dict_by_reg_exp(self):
        expected = {
            "x_00": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            "x_01": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            "x_10": np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
            "x_11": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        }
        result = self.__class__.s.get_compound_dict_by_reg_exp("x_[01][01]")
        for key, array in expected.items():
            self.assertTrue(np.array_equal(result[key], array))

    def test_get_label_at_position(self):
        expected = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
        result = self.__class__.s.get_label_at_position("x", 0)
        self.assertTrue(np.array_equal(expected, result))

    def test_get_num_label(self):
        expected = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        result = self.__class__.s.get_num_label("x", 0)
        self.assertTrue(np.array_equal(expected, result))

        expected = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        result = self.__class__.s.get_num_label("x", 1)
        self.assertTrue(np.array_equal(expected, result))

        expected = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        result = self.__class__.s.get_num_label("x", 2)
        self.assertTrue(np.array_equal(expected, result))

    def test_get_variables(self):
        expected = [np.array([0.0, 0.0]), np.array([0.0, 0.0])]
        result = self.__class__.s.get_variables(["x_00", "y_00"], 1, 3)
        self.assertTrue(np.array_equal(expected, result))

    def test_get_variables_dict(self):
        expected = {"x_00": np.array([0.0, 0.0]), "y_00": np.array([0.0, 0.0])}
        result = self.__class__.s.get_variables_dict(["x_00", "y_00"], 1, 3)
        for key, array in expected.items():
            self.assertTrue(np.array_equal(result[key], array))

    def test_get_variables_df(self):
        expected = np.array([0.0, 0.0])
        result = self.__class__.s.get_variables_df(["x_00", "y_00"], 1, 3)[
            "x_00"
        ].values
        self.assertTrue(np.array_equal(expected, result))


if __name__ == "__main__":
    unittest.main()
