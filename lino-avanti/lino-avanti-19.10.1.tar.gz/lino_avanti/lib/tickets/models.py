# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino_xl.lib.tickets.models import *
from lino.api import _

Ticket.hide_elements('closed')

# class Ticket(Ticket):
#     class Meta(Ticket.Meta):
#         app_label = 'tickets'
#         abstract = dd.is_abstract_model(__name__, 'Ticket')

#     client = dd.ForeignKey('avanti.Client', blank=True, null=True)


dd.update_field(
    'tickets.Ticket', 'upgrade_notes', verbose_name=_("Solution"))

# dd.update_field(
#     'tickets.Ticket', 'state', default=TicketStates.todo.as_callable)

class TicketDetail(TicketDetail):
    main = "general #history_tab more"

    general = dd.Panel("""
    summary:40 end_user
    id:6 user:12 
    workflow_buttons
    description
    """, label=_("General"))

    # history_tab = dd.Panel("""
    # changes.ChangesByMaster:50 #stars.StarsByController:20
    # """, label=_("History"), required_roles=dd.login_required(Triager))

    more = dd.Panel("""
    more1:60 
    upgrade_notes:20
    """, label=_("More"), required_roles=dd.login_required(Triager))

    more1 = """
    created modified ticket_type:10
    deadline site 
    state priority project
    # standby feedback closed
    """



Tickets.detail_layout = TicketDetail()


