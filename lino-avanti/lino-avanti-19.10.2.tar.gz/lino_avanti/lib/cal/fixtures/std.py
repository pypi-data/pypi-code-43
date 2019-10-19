from lino.api import rt, dd, _

from lino_xl.lib.cal.fixtures.std import objects as std_objects

def reason(desig):
    return rt.models.cal.AbsenceReason(**dd.str2kw('designation', desig))

def objects():
    yield std_objects()
    yield reason(_("Sickness"))
    yield reason(_("Other valid reason"))
    yield reason(_("Unknown"))
    yield reason(_("Unjustified"))
