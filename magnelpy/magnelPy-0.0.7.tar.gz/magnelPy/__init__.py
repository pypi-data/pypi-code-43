"""
magnelPy
========
Provides
  1. Support methods for data handling
  2. Probabilistic / Reliability methods and tools
  3. Structural Fire Engineering methods and tools

Available subpackages
---------------------
SFE
  Structural Fire Engineering codes and tools

Available Utilities
---------------------
admin
	Basic functions for data handling : read-write to excel etc.
stochVar
	Standard formatting of stochastic variables.
statFunc
	Probabilistic distribution evaluations in standardized format.
sampling
	Sampling procedures.

Documentation
-------------
The documentation is incomplete and under development.

Code snippets are indicated by three greater-than signs:
  >>> x = 42
  >>> x = x + 1

Use the built-in ``help`` function to view a function's docstring:
  >>> help(magnelPy)

"""

### standard imports ###
# makes e.g. magnelPy.statFunc directly available when >>> import magnelPy
from magnelPy import statFunc
