from sensiml.client import SensiML
from sensiml.widgets import DashBoard


try:
    from IPython.core.display import HTML

    display(HTML("<style>.container { width:90% !important; }</style>"))
except:
    pass

name = "sensiml"


__version__ = "2019.3.5"
__all__ = ["SensiML", "DashBoard"]
