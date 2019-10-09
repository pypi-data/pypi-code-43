# necessary for this directory to be a module
# __init__.py

from libHREELS.HREELS import HREELS
from libHREELS.HREELS import offset, createDataDictionary, HREELS_elog_Dictionary
from libHREELS.LEED import LEED, LEED_elog_Dictionary
from libHREELS.Auger.Auger import Auger, Auger_elog_Dictionary
from libHREELS.ViewHREELS import HREELS_Window
import libHREELS.ViewHREELS as ViewHREELS
import libHREELS.ViewAuger as ViewAuger

# __all__ = ["HREELS","LEED", "Auger/Auger", "ViewHREELS"]

__version__ = '0.3.0'
