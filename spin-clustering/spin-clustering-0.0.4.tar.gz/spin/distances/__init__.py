"""Distances module with utilities to compute distances.

Distances module implement common distances functions for multiple sets of
vectors and distance utilities to fast compute distances between vectors. It
makes heavy use of numpy vectorization capabilities to ensure fast calculation
time.
"""

from .distances import l2_distance_matrix


__all__ = [
        "l2_distance_matrix"
        ]
