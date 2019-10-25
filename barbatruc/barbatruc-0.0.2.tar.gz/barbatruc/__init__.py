"""
The CFD solvers
===============

Provides source code of 2D CFD solver.
The content is limited for the moment to Finite Differences.

Differenciation is done in *fd_operators*.
The actual Navier-Stokes solver is in *fd_ns_2d*.

"""
from .fd_ns_2d import *
from .fd_operators import *
from .fluid_domain import *
