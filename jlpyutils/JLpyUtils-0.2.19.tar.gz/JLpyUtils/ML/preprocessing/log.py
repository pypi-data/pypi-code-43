"""
Scalers related to various types of log transformations
"""
import numpy as _np

class log1p():
    def __init__(self):
        """
        Scale data using the natural logarithm of one plus the input array.
        Calculates ``log(1 + x)``.
        """
        pass
    
    def fit_transform(self, X):
        return _np.log1p(X)
    
    def inverse_transform(self, X):
        return _np.expm1(X)
    
class log10_1p():
    def __init__(self):
        """
        Scale data using the logarithm base 10 of one plus the input array.
        Calculates ``log10(1 + x)``.
        """
        pass
    
    def fit_transform(self, X):
        return _np.log10(1+X)
    
    def inverse_transform(self, X):
        return (10**(X))-1
    