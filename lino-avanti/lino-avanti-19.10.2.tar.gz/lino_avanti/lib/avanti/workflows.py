# -*- coding: UTF-8 -*-
# Copyright 2017-2018 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

"""Default workflows for Lino Avanti.

This can be used as :attr:`workflows_module
<lino.core.site.Site.workflows_module>`

"""

# calendar events and presences:
from lino_xl.lib.cal.workflows.voga import *

from lino_avanti.lib.courses.workflows import *

from lino.api import _

from lino_xl.lib.clients.choicelists import KnownContactTypes
KnownContactTypes.clear()
add = KnownContactTypes.add_item

add('10', _("Health insurance"), 'health_insurance')
add('20', _("School"), 'school')
add('30', _("Pharmacy"), 'pharmacy')
add('40', _("Public Center for Social Welfare"), 'social_center')
# add('40', _("General social assistant"), 'general_assistant')
# code 50 might still exist in their database but should be replaced by 40:
# in your restore.py function create_clients_clientcontacttype() say ::
# if known_contact_type == '50': known_contact_type = '40'
# add('50', _("Integration assistant"), 'unused_integ_assistant')
add('60', _("Work consultant"), 'work_consultant')


# same as in voga except that we remove transition to "excused"
GuestStates.clear_transitions()
GuestStates.present.add_transition(
    # "\u2611",  # BALLOT BOX WITH CHECK
    required_states='invited')
    # help_text=_("Participant was present."))

GuestStates.missing.add_transition(
    # "☉",  # 2609 SUN
    required_states='invited')
    # help_text=_("Participant was absent."))

# GuestStates.excused.add_transition(
#     # "⚕",  # 2695
#     required_states='invited')

GuestStates.invited.add_transition(
    # "☐",  # BALLOT BOX \u2610
    required_states='missing present excused')
    # help_text=_("Reset state to invited."))
