

from __future__ import print_function

import math
import tempfile
from os.path import dirname, join

import numpy as np
import vtk

import pyconrad.autoinit
import pyconrad._vtk


_ = pyconrad.ClassGetter()


def test_distance_between_points():

    p0 = (0, 0, 0)
    p1 = (1, 1, 1)

    distSquared = vtk.vtkMath.Distance2BetweenPoints(p0, p1)

    dist = math.sqrt(distSquared)

    print("p0 = ", p0)
    print("p1 = ", p1)
    print("distance squared = ", distSquared)
    print("distance = ", dist)


def test_read_vti():
    path = join(dirname(__file__), 'small_domain.vti')
    grid = _.NumericGrid.from_vtk(path)
    print(grid)
    print(grid.origin)
    print(grid.spacing)


# def test_write_vtk():
#     random_array = np.random.rand(23, 12)
#     random_origin = np.random.rand(3)
#     random_spacing = np.random.rand(3)
#     temp_vtk = tempfile.NamedTemporaryFile(suffix=".vtk").name

#     pyconrad._vtk.write_vkt(temp_vtk, random_array,
#                             random_spacing, random_origin)


def test_write_read_vti():
    random_array = np.random.rand(23, 12, 5)
    random_origin = np.random.rand(3)
    random_spacing = np.random.rand(3)
    temp_vti =  tempfile.NamedTemporaryFile(suffix=".vti").name
    print('Temporal file: ' + temp_vti)

    grid = _.NumericGrid.from_numpy(random_array)
    grid.setOrigin(random_origin)
    grid.setSpacing(random_spacing)
    grid.save_vtk(temp_vti)


    new_grid = _.NumericGrid.from_vtk(temp_vti)

    assert np.allclose(grid.spacing, new_grid.spacing)
    assert np.allclose(grid.origin, new_grid.origin)
    assert np.allclose(grid.as_numpy(), new_grid.as_numpy())


# def test_write_read_vtk():
#     random_array = np.random.rand(23, 12)
#     random_origin = np.random.rand(2)
#     random_spacing = np.random.rand(2)
#     grid = _.NumericGrid.from_numpy(random_array)
#     grid.setOrigin(random_origin)
#     grid.setSpacing(random_spacing)
#     temp_vti = tempfile.NamedTemporaryFile(suffix=".vtk").name

#     grid = _.NumericGrid.from_numpy(random_array)
#     grid.save_vtk(temp_vti)

#     new_grid = _.NumericGrid.from_vtk(temp_vti)

#     assert np.allclose(grid.spacing, new_grid.spacing)
#     assert np.allclose(grid.origin, new_grid.origin)
#     assert np.allclose(grid.as_numpy(), new_grid.as_numpy())


if __name__ == "__main__":
    test_distance_between_points()
    # test_read_vti()
    # test_write_vtk()
    test_write_read_vti()
    # test_write_read_vtk()
