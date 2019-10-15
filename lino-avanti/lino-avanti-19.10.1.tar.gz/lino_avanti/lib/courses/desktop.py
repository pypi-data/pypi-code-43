# Copyright 2017-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from decimal import Decimal
from lino_xl.lib.courses.desktop import *
from lino.api import _

from lino.core.gfks import gfk2lookup
from lino.utils import join_elems
from etgen.html import E
from lino.modlib.users.mixins import My
from lino_avanti.lib.avanti.roles import ClientsUser
from lino_xl.lib.coachings.roles import CoachingsUser


# Courses.required_roles = dd.login_required(Explorer)


# class LinesByProvider(Lines):
#     master_key = 'provider'

AllActivities.column_names = "line:20 start_date:8 teacher user " \
                             "weekdays_text:10 times_text:10"


AllEnrolments.column_names = "id request_date start_date end_date \
user course pupil pupil__birth_date pupil__age pupil__country \
pupil__city pupil__gender"


class DitchingEnrolments(Enrolments):
    label = _("Absence control")
    order_by = ['-missing_rate', 'pupil']
    column_names = "missing_rate pupil course pupil__user *"
    required_roles = dd.login_required(CoachingsUser)
    params_layout = "coached_by min_missing_rate course_state state author participants_only"
    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(DitchingEnrolments, self).param_defaults(ar, **kw)
        kw['coached_by'] = ar.get_user()
        kw['course_state'] = rt.models.courses.CourseStates.active
        kw['participants_only'] = True
        kw['min_missing_rate'] = Decimal(10)
        return kw

    @classmethod
    def get_request_queryset(self, ar, **kwargs):
        qs = super(DitchingEnrolments, self).get_request_queryset(ar, **kwargs)
        if isinstance(qs, list):
            return qs
        pv = ar.param_values
        if pv.coached_by is not None:
            qs = qs.filter(pupil__user=pv.coached_by)
        if pv.min_missing_rate:
            qs = qs.filter(missing_rate__gte=pv.min_missing_rate)
        return qs

    

class EnrolmentsByCourse(EnrolmentsByCourse):
    column_names = 'id request_date pupil pupil__gender pupil__nationality:15 ' \
                   'needs_childcare needs_school needs_bus needs_evening '\
                   'remark missing_rate workflow_buttons *'

class PresencesByEnrolment(dd.Table):
    model = 'cal.Guest'
    master = 'courses.Enrolment'
    column_names = "event event__state workflow_buttons absence_reason remark *"
    display_mode = "summary"
    order_by = ['event__start_date', 'event__start_time']

    @classmethod
    def get_filter_kw(self, ar, **kw):
        Event = rt.models.cal.Event
        enr = ar.master_instance
        if enr is None:
            return None
        for k, v in gfk2lookup(Event.owner, enr.course).items():
            kw['event__'+k] = v
        kw.update(partner=enr.pupil)
        return super(PresencesByEnrolment, self).get_filter_kw(ar, **kw)

    @classmethod
    def get_table_summary(self, obj, ar):
        if ar is None:
            return ''
        sar = self.request_from(ar, master_instance=obj)

        coll = {}
        for obj in sar:
            if obj.state in coll:
                coll[obj.state] += 1
            else:
                coll[obj.state] = 1
                
        ul = []
        for st in rt.models.cal.GuestStates.get_list_items():
            ul.append(_("{} : {}").format(st, coll.get(st, 0)))
        # elems = join_elems(ul, sep=', ')
        elems = join_elems(ul, sep=E.br)
        return ar.html_text(E.div(*elems))
        # return E.div(class_="htmlText", *elems)

# class CourseDetail(CourseDetail):
#     main = "general cal_tab enrolments"
    
#     general = dd.Panel("""
#     line teacher start_date end_date start_time end_time
#     room #slot workflow_buttons id:8 user
#     name
#     description
#     """, label=_("General"))
    
#     cal_tab = dd.Panel("""
#     max_events max_date every_unit every
#     monday tuesday wednesday thursday friday saturday sunday
#     cal.EntriesByController
#     """, label=_("Calendar"))

#     enrolments_top = 'enrolments_until max_places:10 confirmed free_places:10 print_actions:15'

#     enrolments = dd.Panel("""
#     enrolments_top
#     EnrolmentsByCourse
#     """, label=_("Enrolments"))

    
Enrolments.detail_layout = """
request_date user start_date end_date
course pupil 
needs_childcare needs_school needs_bus needs_evening
remark:40 workflow_buttons:40 printed:20 missing_rate:10
confirmation_details PresencesByEnrolment  RemindersByEnrolment
"""

class CoursesPlanning(Activities):
    required_roles = dd.login_required(CoursesUser)
    label = _("Course planning")
    column_names = \
        "detail_link state "\
        "max_places requested confirmed trying free_places " \
        "school_needed childcare_needed bus_needed evening_needed *"


class Reminders(dd.Table):
    required_roles = dd.login_required(ClientsUser)
    model = 'courses.Reminder'
    order_by = ['-date_issued']


class MyReminders(My, Reminders):
    can_create = False
    # pass

class RemindersByEnrolment(Reminders):
    column_names = 'date_issued degree remark workflow_buttons *'
    auto_fit_column_widths = True
    stay_in_grid = True
    master_key = 'enrolment'
    display_mode = 'summary'
    # can_create = True
    insert_layout = dd.InsertLayout("""
    degree 
    remark
    text_body
    """, window_size=(50,13))
    detail_layout = dd.DetailLayout("""
    date_issued degree workflow_buttons
    remark
    enrolment user id printed
    text_body
    """, window_size=(80,20))
    
    
class RemindersByPupil(Reminders):
    column_names = 'date_issued enrolment user remark workflow_buttons *'
    auto_fit_column_widths = True
    # master = pupil_model
    master_key = 'enrolment__pupil'

    # @classmethod
    # def get_filter_kw(self, ar, **kw):
    #     kw.update(enrolment__pupil=ar.master_instance)
    #     return kw

   
    
