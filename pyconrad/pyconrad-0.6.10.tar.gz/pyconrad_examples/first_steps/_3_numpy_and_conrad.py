
# Copyright (C) 2010-2017 - Andreas Maier
# CONRAD is developed as an Open Source project under the GNU General Public License (GPL-3.0)
from pyconrad import setup_pyconrad, java_float_dtype, JArray, JDouble, ClassGetter
import pyconrad
import numpy as np

# Setup pyconrad explicitly specifying RAM for JVM, dev_dirs can be your custom CONRAD, CONRADRSL directory
pyconrad.setup_pyconrad(min_ram='500M', max_ram='8G', dev_dirs=[])
# ClassGetter provides basic classes like PointND, SimpleVector, SimpleMatrix, GridND without any imports
_ = ClassGetter()


array = np.random.rand(4, 2, 3).astype(pyconrad.java_float_dtype)
grid = _.NumericGrid.from_numpy(array)



# Manipulate data in using CONRAD at Position (x,y,z) = (0,1,3)
grid.setValue(5.0, [0, 1, 3])
# or easier with Python indices (reversed)
grid[3,1,0] = 5

# Shape is for dimensions (z,y,x), size for (x,y,z) 
print(grid.shape)
print(grid.size)

# Get modified array
new_array = grid.as_numpy()

# Attention: Python has a different indexing (z,y,x)
print('Old value: %f' % array[3, 1, 0])
print('New value: %f' % new_array[3, 1, 0])

# Test extention methods to create from numpy and to convert to numpy: PointND
java_point = _.PointND([2.1, 3.1])
java_point2 = _.PointND.from_numpy(np.array([2.1, 3.1]))
java_point3 = _.PointND.from_list([2.1, 3.1])
numpy_point = java_point.as_numpy()
numpy_point2 = java_point2.as_numpy()
numpy_point3 = java_point3.as_numpy()

# Test extention methods to create from numpy and to convert to numpy: SimpleVector
java_vector = _.SimpleVector(JArray(JDouble)([2.1, 3.1]))
java_vector2 = _.SimpleVector.from_numpy(np.array([2.1, 3.1]))
java_vector3 = _.SimpleVector.from_list([2.1, 3.1])
numpy_vector = java_vector.as_numpy()
numpy_vector2 = np.array(java_vector2)
numpy_vector3 = java_vector3.as_numpy()

# Test extention methods to create from numpy and to convert to numpy: SimpleMatrix
java_matrix = _.SimpleMatrix(
    JArray(JDouble, 2)([[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]]))
java_matrix2 = _.SimpleMatrix.from_numpy(
    np.array([[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]]))
java_matrix3 = _.SimpleMatrix.from_list(
    [[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]])
numpy_matrix = java_matrix.as_numpy()
numpy_matrix2 = java_matrix2.as_numpy()
numpy_matrix3 = java_matrix3.as_numpy()

_.add_namespaces('edu.stanford.rsl.tutorial.phantoms')
phantom = _.MickeyMouseGrid2D(200, 200)

# extension methods are added tu numeric grid, which is the parent class of Grid1D, Grid2D, Grid3D,...
_.add_namespaces("edu.stanford.rsl.conrad.data.numeric")
java_grid3D = _.Grid3D(100, 100, 100)
java_grid3D2 = _.Grid3D.from_numpy(
    np.array([[[2.1, 3.1], [2.2, 3.2], [2.3, 3.3]]]))
java_grid3D3 = _.Grid3D.from_list(
    [[[2.1, 3.1], [2.2, 3.2], [2.3, 3.3]]])

np_grid3D = java_grid3D.as_numpy()
np_grid3D2 = java_grid3D2.as_numpy()
np_grid3D3 = java_grid3D3.as_numpy()

