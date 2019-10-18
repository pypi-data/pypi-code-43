"""This is a small module for generating sets of function signatures
and corresponding function objects. This is useful in unit testing.

"""

from .main import (valid_signatures,
                   all_valid_signatures,
                   valid_parameters,
                   valid_functions,
                   all_valid_functions)

__all__ = ['valid_parameters',
           'valid_signatures',
           'all_valid_signatures',
           'valid_functions',
           'all_valid_functions']
