# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""Desktop UI for this plugin.

"""

from lino.modlib.users.desktop import *
from lino.modlib.office.roles import OfficeUser

from lino.api import dd, _


class UserDetail(UserDetail):
    """Layout of User Detail in Lino Avanti."""

    main = "general calendar dashboard.WidgetsByUser #coaching"

    general = dd.Panel("""
    box1:40 #MembershipsByUser:20 AuthoritiesGiven:20
    remarks:40 AuthoritiesTaken:20
    """, label=_("General"))

    box1 = """
    username user_type:20 partner
    first_name last_name initials
    email language mail_mode
    id created modified
    """

    calendar = dd.Panel("""
    cal_left:30 cal.TasksByUser:60
    """, label=dd.plugins.cal.verbose_name, required_roles=dd.login_required(OfficeUser))

    cal_left = """
    event_type access_class
    cal.SubscriptionsByUser
    # cal.MembershipsByUser
    """

    coaching = dd.Panel("""
    coaching_type coaching_supervisor
    coachings.CoachingsByUser:40
    """, label=_("Coaching"))


Users.detail_layout = UserDetail()
