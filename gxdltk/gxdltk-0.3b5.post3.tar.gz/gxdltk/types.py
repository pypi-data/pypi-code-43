"""
Enums in RNN
"""

from enum import Enum,unique

__all__ = ["RNNTypes"]

@unique
class RNNTypes(Enum):
    """
    Provide convenience way for selecting types
    """
    lstm = 0
    bi_lstm = 1
    gru = 2
    bi_gru = 3
