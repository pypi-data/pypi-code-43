#!/usr/bin/env python3

# Use numpy as backend for storing data
import numpy as np
import numbers
import os

# Define the state class
class state(np.ndarray):

    # Class initializers
    def __new__(cls, input_array):
        return np.asarray(input_array).view(cls)

    # Define the transpose operator
    @property
    def T(self):
        """Returns the transpose of the class"""

        if isinstance(self, bra):
            # bra becomes a ket
            return ket(self)

        elif isinstance(self, ket):
            # ket becomes a bra
            return bra(self)

        elif isinstance(self, operator):
            # Operator stays operator
            return super().T

        else:
            raise NotImplementedError

    def transpose(self, *args, **kwargs):
        """Returns the transpose of the class"""

        return self.T

    # Define the hermitian transpose operator
    @property
    def H(self):
        """Returns the hermitian conjugate of the class"""

        if isinstance(self, bra):
            # bra becomes a ket
            return ket(np.conj(self))

        elif isinstance(self, ket):
            # ket becomes a bra
            return bra(np.conj(self))

        elif isinstance(self, operator):
            # Operator stays operator
            return operator(np.conj(self.T))

        else:
            raise NotImplementedError

    # Define conversion to probability
    def prob(self):
        """returns a numpy.ndarray containing the values |v_i|^2
        (Only works on bra or a ket)"""

        # This function is only defined for a bra or a ket
        if isinstance(self, bra) or isinstance(self, ket):
            return np.real(np.multiply(self, np.conj(self))).view(np.ndarray)
        else:
            raise NotImplementedError

    # Overload the np.sum function
    def sum(self, *args, **kwargs):
        return np.sum(np.array(self))

    # Overload the np.diagonal function
    def diagonal(self, offset=None, axis1=None, axis2=None):
        return np.diagonal(np.array(self), offset, axis1, axis2)

    # Return a string representation of the data in the state
    def array_str(self):

        # Format based on type
        if isinstance(self, bra) or isinstance(self, operator):
            # Get horizontally formatted string
            return np.array_str(self, precision=4, suppress_small=True)

        elif isinstance(self, ket):
            # Get vertically formatted string
            return np.array_str(np.reshape(self, (self.size, 1)), precision=4, suppress_small=True)
        else:
            NotImplementedError

    # Define the addition operators
    def __add__(self, other):

        # Compare the types
        if type(self) == type(other):
            # If they have same type, addition can be made
            return super().__add__(other)

        elif isinstance(other, numbers.Number):
            # If it is just a number, just add each value
            return super().__add__(other)

        else:
            # If the have different type, addition is not defined
            raise Exception('Must have same type! Cannot add ket and bra')

    # Define the subtraction operator
    def __sub__(self, other):

        # Compare the types
        if type(self) == type(other):
            # If they have same type, subtraction can be made
            return super().__sub__(other)

        elif isinstance(other, numbers.Number):
            # If it is just a number, just subtract each value
            return super().__sub__(other)

        elif isinstance(self, (bra, ket)) and isinstance(other, (bra, ket)):
            # If the have different type (bra vs ket), subtraction is not defined
            raise Exception('Must have same type! Cannot subtract ket and bra')

        elif isinstance(self, (bra, ket, operator)) and isinstance(other, (bra, ket, operator)):
            # If the have different type (bra/ket vs operator), subtraction is not defined
            raise Exception('Must have same type! Cannot subtract ket/bra and operator')

        else:
            # Unknown types
            raise NotImplementedError

    # Define the multiplication operator
    def __mul__(self, other):

        # The type of the objects determines how multiplication is done
        if isinstance(self, bra) and isinstance(other, ket):
            # Compute the inner product
            return np.dot(self, other)

        elif isinstance(self, ket) and isinstance(other, bra):
            # Compute the outer product
            return operator(np.outer(self, other))

        elif isinstance(self, bra) and isinstance(other, operator):
            # Compute the matrix multiplication
            return bra(np.dot(self, other))

        elif isinstance(self, operator) and isinstance(other, ket):
            # Compute the matrix multiplication
            return ket(np.dot(self, other))

        elif isinstance(self, operator) and isinstance(other, operator):
            # Compute the matrix multiplication
            return operator(np.dot(self, other))

        elif isinstance(other, numbers.Number):
            # Otherwise, just multiply each value
            return super().__mul__(other)

        # If the have same type, multiplication is not defined
        elif isinstance(self, bra) and isinstance(other, bra):
            raise Exception('Must have different type! Cannot evaluate <v|<v|')
        elif isinstance(self, ket) and isinstance(other, ket):
            raise Exception('Must have different type! Cannot evaluate |v>|v>')

        else:
            raise NotImplementedError

    # Define representation
    def __repr__(self):
        if isinstance(self, bra) or isinstance(self, ket):
            return self.__name__() + '(' + np.array_str(self, precision=4, suppress_small=True) + ')'
        elif isinstance(self, operator):
            return self.__name__() + '(' + str.replace(np.array_str(self, precision=4, suppress_small=True), '\n', '\n         ') + ')'
        elif isinstance(self, state):
            return np.array_str(self, precision=4, suppress_small=True)
        else:
            raise NotImplementedError

# Define the bra class
class bra(state):
    """The bra state <v| is a vector like numpy.ndarray that follows the rules
    of Dirac notation.
    Beyond the numpy methods of numpy.ndarray, It has the following methods:

    .prob() - returns a numpy.ndarray containing the values |v_i|^2  """

    # Class initializer
    def __new__(self, data):
        # Copy the parents information
        return super().__new__(bra, verify_data_format(data))

    # Define print string
    def __str__(self):
        # Format the output to show bra notation
        return '<v| = ' + self.array_str()

    # Define name
    def __name__(self):
        return 'bra'

# Define the ket class
class ket(state):
    """The ket state |v> is a vector like numpy.ndarray that follows the rules
    of Dirac notation.
    Beyond the numpy methods of numpy.ndarray, It has the following methods:

    .prob() - returns a numpy.ndarray containing the values |v_i|^2  """

    # Class initializer
    def __new__(self, data):
        # Copy the parents information
        return super().__new__(ket, verify_data_format(data))

    # Define print string
    def __str__(self):
        # Format the output to show ket notation
        return '|v> = ' + str.replace(self.array_str(), '\n', '\n      ')

    # Define name
    def __name__(self):
        return 'ket'

    # Define representation
    def __repr__(self):
        # Format the output to show ket notation
        return 'ket(' + str.replace(self.array_str(), '\n', '\n    ')

# Define the operator class
class operator(state):
    """The operator state O is a matrix like numpy.ndarray that follows the rules
    of Dirac notation.
    Beyond the numpy methods of numpy.ndarray, It has the following methods:

    .eig() - returns a tuple containing:
        1) numpy.ndarray with the (sorted) eigenvalues,
        2) An operator containing the (sorted) eigenvectors
           e.g. the first eigenvector is a bra located at index O[0]"""

    def __new__(self, data):
        # Copy the parents information
        return super().__new__(operator, verify_data_format(data, dim='operator'))

    # Define eigenvalue function
    def eig(self):
        """Computes and sorts the eigenvalues and eigenvectors of the operator using
        numpy.linalg.eig()"""

        # Use numpy to compute eigenvalues and eigenvectors
        w, v = np.linalg.eig(self)

        # Sort eigenvalues and eigenvectors according to eigenvalue
        I = np.argsort(w)
        w = w[I]
        v = v[:, I]

        return w, v

    # Define print string
    def __str__(self):
        # Format the output to show operator notation
        return u'O = ' + str.replace(np.array_str(self, precision=4, suppress_small=True), '\n', '\n    ')

    # Define name
    def __name__(self):
        return 'operator'

    # Overwrite the index operators
    def __getitem__(self, index):

        # User has given slice
        if isinstance(index, tuple):

            # Tuple has more than two inputs
            if np.size(index) > 2:
                raise Exception('Operator is 2D')

            # User requests horizontal silce
            elif isinstance(index[1],slice) and isinstance(index[0],int) :
                return bra(super().__getitem__(index))

            # User requests vertical slice
            elif isinstance(index[0],slice)  and isinstance(index[1],int) :
                return ket(super().__getitem__(index))

            # User requests 2D slice
            else :
                return super().__getitem__(index)

        # User has given scalar
        else:
            return ket(super().__getitem__((slice(None,None,None),index)))

# Define function to verify the data inputs
def verify_data_format(data, dim='1D'):

    # Convert lists to numpy arrays
    if isinstance(data, list):
        data = np.array(data)

    if isinstance(data, np.ndarray):  # In numpy array format, reshape to be shape (N,) or (N,N)

        # Get current shape
        shape = np.shape(data)

        # data is numpy 1-D type and already the right format
        if np.size(shape) == 1 and dim == '1D':
            return data

        # data is 2-D type
        elif np.size(shape) == 2:
            dx, dy = sorted(shape)

            # Process 1D data types
            if dim == '1D':

                # verify data is 1D
                if dx != 1:
                    raise Exception(
                        'Input must be 1-D. Are you trying to make an operator?')

                # Reshape the output to be of shape (N,)
                return np.reshape(data, (dy,))

            elif dim == 'operator':

                # Verify data is a square matrix
                if dx != dy:
                    raise Exception('Input must be a square matrix')

                # Cast boolean inputs to integer
                if data.dtype == np.dtype('bool'):
                    data = data.astype(int)

                # Reshape the output to be of shape (N,N)
                return data

            # Type not recognized
            else:
                raise NotImplementedError

        # Data type unknown
        else:
            raise NotImplementedError

# Define video writer function
def make_video(fmtstr, outputname='video.mp4', framerate=30):
    """make_video() calls the external library FFmpeg to write images into a video

    Parameters
    ---------------------------------------
    - fmtstr : includes information of where the images are stored and how they are named
        example 1: fmtstr = 'video/%3d.png'
        example 2: fmtstr = 'video/'
    - outputname : lets you set the name of the video
    - framerate : controls the framerate"""

    # Generate an output path
    outputpath = fmtstr.split('/')
    # Does the path end with an image format?
    fmt = outputpath[-1].split('.')
    if fmt[-1].lower() in ['jpg', 'jpeg', 'tif', 'tiff', 'png'] :
        outputpath[-1] = outputname
        outputpath = '/'.join(outputpath)

    # Else assume path is just a folder
    else :
        if fmtstr[-1] == '/' :
            outputpath = fmtstr + outputname
        else :
            outputpath = fmtstr + '/' + outputname

    # Check that ffmpeg is installed
    f = os.system('ffmpeg -version')

    if f != 0:
        raise Exception('Could not use ffmpeg. Are you sure it is installed?')

    # Attempt to compile video
    f = os.system('ffmpeg -r %d -f image2 -i %s -vcodec libx264 -crf 25 -pix_fmt yuv420p %s -y' % (framerate, fmtstr, outputpath))

    if f != 0:
        raise Exception('Error using ffmpeg. Is the input correctly formatted?')


# Define a few useful quantities
c = 299792458                   # [m / s]   Speed of light
h = 6.62606896e-34              # [J]       Planck Constant
hbar = 1.054571628e-34          # [J]       Planck Constant / 2 pi (Diracs constant)
eV = 1.602176565e-19            # [J]       Electron Volt
m_electron = 9.10938356e-31     # [kg]      Mass of electron
pi = np.pi                      # Pi
