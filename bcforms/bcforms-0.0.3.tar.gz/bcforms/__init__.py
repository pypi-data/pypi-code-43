import pkg_resources

# read version
with open(pkg_resources.resource_filename('bcforms', 'VERSION'), 'r') as file:
    __version__ = file.read().strip()

from .core import Atom, Crosslink, BcForm, Subunit, OntologyCrosslink
