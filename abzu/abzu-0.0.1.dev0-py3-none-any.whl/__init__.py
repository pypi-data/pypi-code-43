# __init__.py

# Version of the package
__version__ = "0.0.1dev0"
__author__ = "Tiago Tresoldi"
__email__ = "tresoldi@shh.mpg.de"

# Build the namespace
from . import kiss

from .textgen import random_labels, random_species
