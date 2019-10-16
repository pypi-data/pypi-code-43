# flake8: noqa

import unittest
from modelbase.core import ParameterModel, ParameterSet


class ParameterTests(unittest.TestCase):
    """Tests for parameter initialization and updates"""

    # Initialization
    def test_parameter_init_empty(self):
        m = ParameterModel()
        self.assertTrue(isinstance(m._parameters, ParameterSet))

    def test_parameter_init_dict(self):
        m = ParameterModel()
        p = {"p1": 1}
        m = ParameterModel(p)
        self.assertEqual(m._parameters.p1, p["p1"])

    def test_parameter_init_parameter_set(self):
        m = ParameterModel()
        p = ParameterSet({"p1": 1})
        m = ParameterModel(p)
        self.assertEqual(m._parameters.p1, p.p1)

    def test_parameter_init_type_error_list(self):
        with self.assertRaises(TypeError):
            m = ParameterModel(list())

    def test_parameter_init_type_error_int(self):
        with self.assertRaises(TypeError):
            m = ParameterModel(int())

    def test_parameter_init_type_error_float(self):
        with self.assertRaises(TypeError):
            m = ParameterModel(float())

    def test_parameter_init_type_error_str(self):
        with self.assertRaises(TypeError):
            m = ParameterModel(str())

    def test_parameter_init_type_error_set(self):
        with self.assertRaises(TypeError):
            m = ParameterModel(set())

    # Add parameters function
    def test_add_parameters_dict(self):
        m = ParameterModel({"p1": 1})
        m.add_parameters({"p2": 2})
        self.assertEqual(m._parameters.p1, 1)
        self.assertEqual(m._parameters.p2, 2)

    def test_add_parameters_parameter_set(self):
        m = ParameterModel({"p1": 1})
        m.add_parameters(ParameterSet({"p2": 2}))
        self.assertEqual(m._parameters.p1, 1)
        self.assertEqual(m._parameters.p2, 2)

    def test_add_parameters_type_error_list(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_parameters(list())

    def test_add_parameters_type_error_int(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_parameters(int())

    def test_add_parameters_type_error_float(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_parameters(float())

    def test_add_parameters_type_error_str(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_parameters(str())

    def test_add_parameters_type_error_set(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_parameters(set())

    def test_add_parameters_existing(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(ValueError):
            m.add_parameters({"p1": 2})

    # Update parameters
    def test_update_parameters_dict(self):
        m = ParameterModel({"p1": 1})
        m.update_parameters({"p1": 2})
        self.assertEqual(m._parameters.p1, 2)

    def test_update_parameters_parameter_set(self):
        m = ParameterModel({"p1": 1})
        m.update_parameters(ParameterSet({"p1": 2}))
        self.assertEqual(m._parameters.p1, 2)

    def test_update_parameters_type_error_list(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.update_parameters(list())

    def test_update_parameters_type_error_int(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.update_parameters(int())

    def test_update_parameters_type_error_float(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.update_parameters(float())

    def test_update_parameters_type_error_str(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.update_parameters(str())

    def test_update_parameters_type_error_set(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.update_parameters(set())

    def test_update_parameters_non_existing(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(ValueError):
            m.update_parameters({"p2": 2})

    # Add and update parameters
    def test_add_and_update_parameters_dict(self):
        m = ParameterModel({"p1": 1})
        m.add_and_update_parameters({"p2": 2})
        self.assertEqual(m._parameters.p1, 1)
        self.assertEqual(m._parameters.p2, 2)

    def test_add_and_update_parameters_parameter_set(self):
        m = ParameterModel({"p1": 1})
        m.add_and_update_parameters(ParameterSet({"p2": 2}))
        self.assertEqual(m._parameters.p1, 1)
        self.assertEqual(m._parameters.p2, 2)

    def test_add_and_update_parameters_type_error_list(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_and_update_parameters(list())

    def test_add_and_update_parameters_type_error_int(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_and_update_parameters(int())

    def test_add_and_update_parameters_type_error_float(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_and_update_parameters(float())

    def test_add_and_update_parameters_type_error_str(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_and_update_parameters(str())

    def test_add_and_update_parameters_type_error_set(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.add_and_update_parameters(set())

    # Remove parameters
    def test_remove_parameters_str(self):
        m = ParameterModel({"p1": 1})
        m.remove_parameters("p1")
        with self.assertRaises(AttributeError):
            m._parameters.p1

    def test_remove_parameters_list(self):
        m = ParameterModel({"p1": 1, "p2": 2})
        m.remove_parameters(["p1", "p2"])
        with self.assertRaises(AttributeError):
            m._parameters.p1
        with self.assertRaises(AttributeError):
            m._parameters.p2

    def test_remove_parameters_type_error_dict(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.remove_parameters(dict())

    def test_remove_parameters_type_error_int(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.remove_parameters(int())

    def test_remove_parameters_type_error_float(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.remove_parameters(float())

    def test_remove_parameters_type_error_set(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(TypeError):
            m.remove_parameters(set())

    def test_remove_parameters_nonexistent(self):
        m = ParameterModel({"p1": 1})
        with self.assertRaises(ValueError):
            m.remove_parameters(str())


if __name__ == "__main__":
    unittest.main()
