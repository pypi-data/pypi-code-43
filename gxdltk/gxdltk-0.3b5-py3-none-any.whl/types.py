"""
Enums in RNN
"""

from enum import Enum,unique

@unique
class RNNTypes(Enum):
    """
    Provide conv way for selecting types
    """
    lstm = 0
    bi_lstm = 1
    gru = 2
    bi_gru = 3
