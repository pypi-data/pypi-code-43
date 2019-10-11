# This is to make 'from EPICS_CA.CA import caget' work.
# Author: Friedrich Schotte
# Date created: 2019-10-02
from .EPICS_CA import CA, CAServer
import sys

sys.modules["EPICS_CA.CA"] = sys.modules["EPICS_CA.EPICS_CA.CA"]
sys.modules["EPICS_CA.CAServer"] = sys.modules["EPICS_CA.EPICS_CA.CAServer"]
