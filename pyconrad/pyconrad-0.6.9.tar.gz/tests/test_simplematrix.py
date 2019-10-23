import pyconrad.autoinit
import numpy as np
from jpype import JArray, JDouble

_ = pyconrad.ClassGetter()


def test_simplematrix():
    matrix = np.array([[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]])
    java_matrix = _.SimpleMatrix.from_numpy(matrix)
    new_matrix = java_matrix.as_numpy()
    
    assert java_matrix.shape == matrix.shape
    assert np.allclose(matrix, new_matrix)


def test_list_to_simplematrix():
    java_matrix = _.SimpleMatrix(
        JArray(JDouble, 2)([[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]]))
    java_matrix2 = _.SimpleMatrix.from_numpy(
        np.array([[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]]))
    java_matrix3 = _.SimpleMatrix.from_list(
        [[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]])
    numpy_matrix = java_matrix.as_numpy()
    numpy_matrix2 = java_matrix2.as_numpy()
    numpy_matrix3 = java_matrix3.as_numpy()

    assert numpy_matrix is not None
    assert numpy_matrix2 is not None
    assert numpy_matrix3 is not None

def main():
    test_list_to_simplematrix()
    test_simplematrix()

if __name__ == '__main__':
    main()
