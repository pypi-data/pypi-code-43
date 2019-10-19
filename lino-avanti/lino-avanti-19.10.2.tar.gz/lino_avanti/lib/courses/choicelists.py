# Copyright 2017-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.api import dd, rt, _

class ReminderStates(dd.Workflow):
    verbose_name = _("State")
    verbose_name_plural = _("Reminder states")

add = ReminderStates.add_item
add("10", _("Draft"), 'draft')
add("20", _("Sent"), 'sent')
add("30", _("OK"), 'ok')
add("40", _("Final"), 'final')
add("90", _("Cancelled"), 'cancelled')


class ReminderDegrees(dd.Workflow):
    verbose_name = _("Degree")
    verbose_name_plural = _("Reminder degrees")

add = ReminderDegrees.add_item
add("10", _("First reminder"), 'first')
add("20", _("Second reminder"), 'second')
add("30", _("Third reminder"), 'third')

