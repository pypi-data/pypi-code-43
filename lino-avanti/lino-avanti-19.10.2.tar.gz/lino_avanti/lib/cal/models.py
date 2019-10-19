# -*- coding: UTF-8 -*-
# Copyright 2013-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals

from lino_xl.lib.cal.models import *

from lino.api import _
from lino.utils.mldbc.mixins import BabelDesignated
from lino.modlib.office.roles import OfficeStaff
from lino_avanti.lib.avanti.roles import ClientsUser


class AbsenceReason(BabelDesignated):
    
    class Meta():
        verbose_name = _("Absence reason")
        verbose_name_plural = _("Absence reasons")
        abstract = dd.is_abstract_model(__name__, 'AbsenceReason')
        

class AbsenceReasons(dd.Table):
    required_roles = dd.login_required(OfficeStaff)
    model = 'cal.AbsenceReason'
    
    
class Guest(Guest):

    class Meta(Guest.Meta):
        abstract = dd.is_abstract_model(__name__, 'Guest')
        
    absence_reason = dd.ForeignKey(
        'cal.AbsenceReason', blank=True, null=True)

    def disabled_fields(self, ar):
        rv = super(Guest, self).disabled_fields(ar)
        if not ar.get_user().user_type.has_required_roles([ClientsUser]):
            rv.add("partner")
        return rv

dd.update_field(Guest, "partner", verbose_name=_("Participant"))

class GuestDetail(dd.DetailLayout):
    window_size = (60, 'auto')
    main = """
    event partner role
    state workflow_buttons 
    absence_reason 
    remark 
    """

GuestsByEvent.column_names = 'partner role workflow_buttons absence_reason remark *'    
AllGuests.column_names = 'partner role workflow_buttons absence_reason remark event *'
