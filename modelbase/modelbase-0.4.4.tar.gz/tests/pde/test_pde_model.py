# flake8: noqa
import unittest
import modelbase.pde as pde
import numpy as np


def get_right_hand_side(self, t, y0):
    return pde.utils.perffuncs.diffusion(
        np.zeros_like(y0),
        y0,
        self._is_celltype_array["a"],
        self.neighbors["a", "a"],
        self.parameters["k"],
        self._n_neighbors,
    )


def get_right_hand_side_two_vars(self, t, y0):
    y1 = y0[: len(y0) // 2]
    y2 = y0[len(y0) // 2 :]

    res1 = pde.utils.perffuncs.diffusion(
        np.zeros_like(y1),
        y1,
        self._is_celltype_array["a"],
        self.neighbors["a", "a"],
        self.parameters["k"],
        self._n_neighbors,
    )

    res2 = pde.utils.perffuncs.diffusion(
        np.zeros_like(y2),
        y2,
        self._is_celltype_array["a"],
        self.neighbors["a", "a"],
        self.parameters["k"],
        self._n_neighbors,
    )
    return np.hstack((res1, res2))


class TestCycParser(unittest.TestCase):
    def test_initialize_cells(self):
        m = pde.basemodels.RodGridModel(10)
        self.assertTrue(np.array_equal(m.cells, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))

    def test_add_celltype(self):
        m = pde.basemodels.RodGridModel(10)
        m.add_celltype("a", 1)
        self.assertTrue(m.celltypes == {"a": 1})

    def test_add_cell(self):
        m = pde.basemodels.RodGridModel(5)
        m.add_celltype("a", 1)
        m.add_cell((2), "a")
        self.assertTrue(np.array_equal(m.cells, [0, 0, 1, 0, 0]))

    def test_add_variable(self):
        m = pde.basemodels.RodGridModel(5)
        m.add_celltype("a", 1)
        m.add_variable("x")
        self.assertTrue(np.array_equal(m.variables, ["x"]))

    def test_get_cell_neighbors_1d(self):
        m = pde.basemodels.RodGridModel(5)
        m.add_celltype("a", 1)
        m.add_cell((2), "a")
        self.assertTrue(np.array_equal(m.get_cell_neighbors(0), [-1, -1]))
        self.assertTrue(np.array_equal(m.get_cell_neighbors(1), [-1, 2]))
        self.assertTrue(np.array_equal(m.get_cell_neighbors(2), [-1, -1]))
        self.assertTrue(np.array_equal(m.get_cell_neighbors(3), [2, -1]))
        self.assertTrue(np.array_equal(m.get_cell_neighbors(4), [-1, -1]))

    def test_get_cell_neighbors_2d(self):
        m = pde.basemodels.SquareGridModel((3, 3))
        m.add_celltype("a", 1)
        m.add_cell((1, 1), "a")
        self.assertTrue(np.array_equal(m.get_cell_neighbors(0), [-1, -1, -1, -1]))
        self.assertTrue(np.array_equal(m.get_cell_neighbors(1), [-1, -1, 4, -1]))
        self.assertTrue(np.array_equal(m.get_cell_neighbors(2), [-1, -1, -1, -1]))
        self.assertTrue(np.array_equal(m.get_cell_neighbors(3), [-1, 4, -1, -1]))
        self.assertTrue(np.array_equal(m.get_cell_neighbors(4), [-1, -1, -1, -1]))
        self.assertTrue(np.array_equal(m.get_cell_neighbors(5), [-1, -1, -1, 4]))
        self.assertTrue(np.array_equal(m.get_cell_neighbors(6), [-1, -1, -1, -1]))
        self.assertTrue(np.array_equal(m.get_cell_neighbors(7), [4, -1, -1, -1]))
        self.assertTrue(np.array_equal(m.get_cell_neighbors(8), [-1, -1, -1, -1]))

    def test_get_cell_neighbors_3d(self):
        m = pde.basemodels.CubeGridModel((3, 3, 3))
        m.add_celltype("a", 1)
        m.add_cell((1, 1, 1), "a")
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(0), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(1), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(2), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(3), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(4), [-1, -1, 13, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(5), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(6), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(7), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(8), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(9), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(10), [-1, 13, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(11), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(12), [-1, -1, -1, -1, 13, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(13), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(14), [-1, -1, -1, -1, -1, 13])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(15), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(16), [-1, -1, -1, 13, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(17), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(18), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(19), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(20), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(21), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(22), [13, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(23), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(24), [-1, -1, -1, -1, -1, -1])
        )
        self.assertTrue(
            np.array_equal(m.get_cell_neighbors(25), [-1, -1, -1, -1, -1, -1])
        )

    def test_initialize_1d(self):
        m = pde.basemodels.RodGridModel(5)
        m.add_celltype("a", 1)
        m.add_cell((1), "a")
        m.add_cell((2), "a")
        m.add_cell((3), "a")
        m.initialize()
        self.assertTrue(
            np.array_equal(
                m.neighbors[("a", "a")], [[-1, -1], [-1, 2], [1, 3], [2, -1], [-1, -1]]
            )
        )

    def test_initialize_2d(self):
        m = pde.basemodels.SquareGridModel((3, 3))
        m.add_celltype("a", 1)
        m.add_cell((1, 1), "a")
        m.add_cell((0, 1), "a")
        m.add_cell((2, 1), "a")
        m.add_cell((1, 2), "a")
        m.add_cell((1, 0), "a")
        m.initialize()
        self.assertTrue(
            np.array_equal(
                m.neighbors[("a", "a")],
                [
                    [-1, -1, -1, -1],
                    [-1, -1, 4, -1],
                    [-1, -1, -1, -1],
                    [-1, 4, -1, -1],
                    [1, 5, 7, 3],
                    [-1, -1, -1, 4],
                    [-1, -1, -1, -1],
                    [4, -1, -1, -1],
                    [-1, -1, -1, -1],
                ],
            )
        )

    def test_initialize_3d(self):
        m = pde.basemodels.CubeGridModel((3, 3, 3))
        m.add_celltype("a", 1)
        m.add_cell((1, 1, 1), "a")
        m.add_cell((2, 1, 1), "a")
        m.add_cell((0, 1, 1), "a")
        m.add_cell((1, 2, 1), "a")
        m.add_cell((1, 0, 1), "a")
        m.add_cell((1, 1, 0), "a")
        m.add_cell((1, 1, 2), "a")
        m.initialize()
        self.assertTrue(
            np.array_equal(
                m.neighbors[("a", "a")],
                [
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, 13, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, 13, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, 13, -1],
                    [4, 16, 22, 10, 14, 12],
                    [-1, -1, -1, -1, -1, 13],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, 13, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [13, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1],
                ],
            )
        )

    def test_right_hand_side_1d(self):
        m = pde.basemodels.RodGridModel(5)
        m.parameters["k"] = 1
        m.add_variable("x")
        m.add_celltype("a", 1)
        m.add_cell((1), "a")
        m.add_cell((2), "a")
        m.add_cell((3), "a")
        m.initialize()
        y0 = m.generate_initial_values()
        y0[2] = 1
        self.assertTrue(
            np.array_equal(get_right_hand_side(m, 0, y0), [0.0, 0.5, -1.0, 0.5, 0.0])
        )

    def test_right_hand_side_2d(self):
        m = pde.basemodels.SquareGridModel((3, 3))
        m.parameters["k"] = 1
        m.add_variable("x")
        m.add_celltype("a", 1)
        m.add_cell((1, 1), "a")
        m.add_cell((0, 1), "a")
        m.add_cell((2, 1), "a")
        m.add_cell((1, 2), "a")
        m.add_cell((1, 0), "a")
        m.initialize()
        y0 = m.generate_initial_values()
        y0[4] = 1
        self.assertTrue(
            np.array_equal(
                get_right_hand_side(m, 0, y0),
                [0.0, 0.25, 0.0, 0.25, -1.0, 0.25, 0.0, 0.25, 0.0],
            )
        )

    def test_right_hand_side_3d(self):
        m = pde.basemodels.CubeGridModel((3, 3, 3))
        m.parameters["k"] = 3
        m.add_variable("x")
        m.add_celltype("a", 1)
        m.add_cell((1, 1, 1), "a")
        m.add_cell((2, 1, 1), "a")
        m.add_cell((0, 1, 1), "a")
        m.add_cell((1, 2, 1), "a")
        m.add_cell((1, 0, 1), "a")
        m.add_cell((1, 1, 0), "a")
        m.add_cell((1, 1, 2), "a")
        m.initialize()
        y0 = m.generate_initial_values()
        y0[13] = 1
        self.assertTrue(
            np.array_equal(
                get_right_hand_side(m, 0, y0),
                [
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    0.5,
                    -3.0,
                    0.5,
                    0.0,
                    0.5,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                ],
            )
        )

    def test_simulation_1d_one_var(self):
        m = pde.basemodels.RodGridModel(5)
        m.parameters["k"] = 1
        m.add_variable("x")
        m.add_celltype("a", 1)
        m.add_cell((1), "a")
        m.add_cell((2), "a")
        m.add_cell((3), "a")
        m.initialize()
        y0 = m.generate_initial_values()
        y0[2] = 1
        setattr(m.__class__, "get_right_hand_side", get_right_hand_side)
        t, y = m.simulate(y0, 1, 2)
        self.assertTrue(t.shape == (2,))
        self.assertTrue(y.shape == (2, 5))

    def test_simulation_1d_two_vars(self):
        m = pde.basemodels.RodGridModel(5)
        m.parameters["k"] = 1
        m.add_variable("x")
        m.add_variable("y")
        m.add_celltype("a", 1)
        m.add_cell((1), "a")
        m.add_cell((2), "a")
        m.add_cell((3), "a")
        m.initialize()
        y0 = m.generate_initial_values()
        y0[2] = 1
        y0[2 + 5] = 2
        setattr(m.__class__, "get_right_hand_side", get_right_hand_side_two_vars)
        t, y1, y2 = m.simulate(y0, 1, 2)
        self.assertTrue(t.shape == (2,))
        self.assertTrue(y1.shape == (2, 5))
        self.assertTrue(y2.shape == (2, 5))

    def test_simulation_2d_one_var(self):
        m = pde.basemodels.SquareGridModel((3, 3))
        m.parameters["k"] = 1
        m.add_variable("x")
        m.add_celltype("a", 1)
        m.add_cell((1, 1), "a")
        m.add_cell((0, 1), "a")
        m.add_cell((2, 1), "a")
        m.add_cell((1, 2), "a")
        m.add_cell((1, 0), "a")
        m.initialize()
        y0 = m.generate_initial_values()
        y0[4] = 1
        setattr(m.__class__, "get_right_hand_side", get_right_hand_side_two_vars)
        t, y = m.simulate(y0, 1, 2)
        self.assertTrue(t.shape == (2,))
        self.assertTrue(y.shape == (2, 3, 3))

    def test_simulation_2d_two_vars(self):
        m = pde.basemodels.SquareGridModel((3, 3))
        m.parameters["k"] = 1
        m.add_variable("x")
        m.add_variable("y")
        m.add_celltype("a", 1)
        m.add_cell((1, 1), "a")
        m.add_cell((0, 1), "a")
        m.add_cell((2, 1), "a")
        m.add_cell((1, 2), "a")
        m.add_cell((1, 0), "a")
        m.initialize()
        y0 = m.generate_initial_values()
        y0[4] = 1
        y0[4 + 9] = 1
        setattr(m.__class__, "get_right_hand_side", get_right_hand_side_two_vars)
        t, y1, y2 = m.simulate(y0, 1, 2)
        self.assertTrue(t.shape == (2,))
        self.assertTrue(y1.shape == (2, 3, 3))
        self.assertTrue(y2.shape == (2, 3, 3))

    def test_simulation_3d_one_var(self):
        m = pde.basemodels.CubeGridModel((3, 3, 3))
        m.parameters["k"] = 3
        m.add_variable("x")
        m.add_celltype("a", 1)
        m.add_cell((1, 1, 1), "a")
        m.add_cell((2, 1, 1), "a")
        m.add_cell((0, 1, 1), "a")
        m.add_cell((1, 2, 1), "a")
        m.add_cell((1, 0, 1), "a")
        m.add_cell((1, 1, 0), "a")
        m.add_cell((1, 1, 2), "a")
        m.initialize()
        y0 = m.generate_initial_values()
        y0[13] = 1
        setattr(m.__class__, "get_right_hand_side", get_right_hand_side)
        t, y = m.simulate(y0, 1, 2)
        self.assertTrue(t.shape == (2,))
        self.assertTrue(y.shape == (2, 3, 3, 3))

    def test_simulation_3d_two_vars(self):
        m = pde.basemodels.CubeGridModel((3, 3, 3))
        m.parameters["k"] = 3
        m.add_variable("x")
        m.add_variable("y")
        m.add_celltype("a", 1)
        m.add_cell((1, 1, 1), "a")
        m.add_cell((2, 1, 1), "a")
        m.add_cell((0, 1, 1), "a")
        m.add_cell((1, 2, 1), "a")
        m.add_cell((1, 0, 1), "a")
        m.add_cell((1, 1, 0), "a")
        m.add_cell((1, 1, 2), "a")
        m.initialize()
        y0 = m.generate_initial_values()
        y0[13] = 1
        y0[13 + 27] = 1
        setattr(m.__class__, "get_right_hand_side", get_right_hand_side_two_vars)
        t, y1, y2 = m.simulate(y0, 1, 2)
        self.assertTrue(t.shape == (2,))
        self.assertTrue(y1.shape == (2, 3, 3, 3))
        self.assertTrue(y2.shape == (2, 3, 3, 3))


if __name__ == "__main__":
    unittest.main()
