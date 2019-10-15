# -*- coding: UTF-8 -*-
# Copyright 2017-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals

from builtins import str
from decimal import Decimal

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext

from etgen.html import E, join_elems

from lino.core.gfks import gfk2lookup
from lino_xl.lib.courses.models import *
from lino.modlib.users.mixins import UserAuthored
from lino_xl.lib.courses.roles import CoursesUser
from lino_xl.lib.excerpts.mixins import Certifiable
from lino_xl.lib.cal.choicelists import EntryStates, GuestStates
from lino_xl.lib.ledger.utils import ZERO, myround
# from lino.modlib.checkdata.choicelists import Checker
# from lino.modlib.summaries.mixins import SimpleSummary
from lino_avanti.lib.avanti.roles import ClientsUser

from .choicelists import ReminderStates, ReminderDegrees

# contacts = dd.resolve_app('contacts')


# class CourseProvider(contacts.Company):

#     """
#     A CourseProvider is a Company that offers Courses. 
#     """
#     class Meta:
#         app_label = 'courses'
#         verbose_name = _("Course provider")
#         verbose_name_plural = _("Course providers")

#     def disable_delete(self, ar=None):
#         # skip the is_imported_partner test
#         return super(contacts.Partner, self).disable_delete(ar)


# class CourseProviderDetail(contacts.CompanyDetail):
#     """Same as CompanyDetail, except that we add a tab
#     :guilabel:`Courses`.

#     """
#     box5 = "remarks"
#     main = "general courses.LinesByProvider"


# class CourseProviders(contacts.Companies):
#     """Table of all course providers

#     """
#     required_roles = dd.login_required(CoursesUser)
#     model = 'courses.CourseProvider'
#     detail_layout = CourseProviderDetail()


# class UpdateMissingRates(dd.Action):
#     label = _("Update missing rates")
#     button_text = ' ☉ '  # like gueststate 'missing'
#     # icon_name = 'lightning'
#     readonly = False

#     def run_from_ui(self, ar, **kw):
#         for obj in ar.selected_rows:
#             obj.run_update_missing_rates()
#         ar.success(refresh=True)


class Course(Course):
    
    class Meta(Course.Meta):
        # app_label = 'courses'
        abstract = dd.is_abstract_model(__name__, 'Course')
        # verbose_name = _("Course")
        # verbose_name_plural = _('Courses')

    @dd.virtualfield(models.IntegerField(_("Bus")))
    def bus_needed(self, ar):
        return self.get_places_sum(
            state=EnrolmentStates.requested, needs_bus=True)

    @dd.virtualfield(models.IntegerField(_("Childcare")))
    def childcare_needed(self, ar):
        return self.get_places_sum(
            state=EnrolmentStates.requested, needs_childcare=True)

    @dd.virtualfield(models.IntegerField(_("Evening")))
    def evening_needed(self, ar):
        return self.get_places_sum(
            state=EnrolmentStates.requested, needs_evening=True)

    @dd.virtualfield(models.IntegerField(_("School")))
    def school_needed(self, ar):
        return self.get_places_sum(
            state=EnrolmentStates.requested, needs_school=True)

    # def update_reminders(self, ar):
    #     super(Course, self).update_reminders(ar)
    #     self.run_update_missing_rates()
        
    @dd.action(label = _("Update missing rates"),
               button_text=' ☉ ')  # like gueststate 'missing'
    def update_missing_rates(self, ar):
        # Event = rt.models.cal.Event
        # expected_states = (EntryStates.took_place, EntryStates.draft)
        # done = Event.objects.filter(
        #     state__in=expected_states,
        #     **gfk2lookup(Event.owner, self)).count()
        
        for obj in self.enrolment_set.all():
            obj.update_missing_rate.run_from_session(ar)
            # obj.update_missing_rate(ar)
            # flt = {'event__'+k: v
            #        for k, v in gfk2lookup(Event.owner, self).items()}

# class Line(Line):
    
#     class Meta(Line.Meta):
#         # app_label = 'courses'
#         abstract = dd.is_abstract_model(__name__, 'Course')
#         verbose_name = pgettext("singular form", "Course line")
#         verbose_name_plural = pgettext("plural form", 'Course lines')

#     provider = dd.ForeignKey(
#         'courses.CourseProvider', blank=True, null=True)
    

class Enrolment(Enrolment):
   
    class Meta(Enrolment.Meta):
        abstract = dd.is_abstract_model(__name__, 'Enrolment')

    needs_childcare = models.BooleanField(_("Childcare"), default=False)
    needs_bus = models.BooleanField(_("Bus"), default=False)
    needs_school = models.BooleanField(_("School"), default=False)
    needs_evening = models.BooleanField(_("Evening"), default=False)

    missing_rate = dd.PriceField(
        _("Missing rate"), default=ZERO, editable=False)
        
    # ending = dd.ForeignKey(
    #     'coachings.CoachingEnding',
    #     related_name="%(app_label)s_%(class)s_set",
    #     blank=True, null=True)


    @dd.virtualfield(dd.HtmlBox(_("Participant")))
    def pupil_info(self, ar):
        txt = self.pupil.get_full_name(nominative=True)
        if ar is None:
            elems = [txt]
        else:
            elems = [ar.obj2html(self.pupil, txt)]
        # elems += [', ']
        # elems += join_elems(
        #     list(self.pupil.address_location_lines()),
        #     sep=', ')
        return E.p(*elems)

    def get_excerpt_title(self):
        return _("Integration Course Agreement")
    
    @classmethod
    def setup_parameters(cls, fields):
        fields.update(
            coached_by=dd.ForeignKey(
                settings.SITE.user_model, verbose_name=_("Coached by"),
                blank=True))
        fields.update(
            min_missing_rate=dd.PriceField(
                _("Missing rate"), blank=True))
        super(Enrolment, cls).setup_parameters(fields)

    @dd.action(label = _("Update missing rate"),
               button_text=' ☉ ')  # like gueststate 'missing'
    def update_missing_rate(self, ar):
        Guest = rt.models.cal.Guest
        Event = rt.models.cal.Event
        # flt = Event.objects.filter(
        #     gfk2lookup(Event.owner, self.course))

        flt = {'event__'+k: v
               for k, v in gfk2lookup(Event.owner, self.course).items()}
        
        flt.update(partner=self.pupil)
        total = Guest.objects.filter(**flt).count()
        if total:
            missing = Guest.objects.filter(
                state__in=(GuestStates.missing,
                           GuestStates.excused), **flt).count()
            self.missing_rate = myround(Decimal(missing*100) / total)
        else:
            self.missing_rate = ZERO
        self.full_clean()
        self.save()
        ar.success(refresh=True)

    def disabled_fields(self, ar):
        rv = super(Enrolment, self).disabled_fields(ar)
        if not ar.get_user().user_type.has_required_roles([ClientsUser]):
            rv.add("pupil")
        return rv


Enrolment.set_widget_options('missing_rate', hide_sum=True)

# dd.update_field(Enrolment, "pupil", verbose_name=_("Participant"))

dd.python_2_unicode_compatible    
class Reminder(UserAuthored, Certifiable):
   
    class Meta:
        verbose_name = _("Reminder")
        verbose_name_plural = _("Reminders")
        abstract = dd.is_abstract_model(__name__, 'Reminder')

    workflow_state_field = 'state'

    enrolment = dd.ForeignKey('courses.Enrolment', editable=False)
    date_issued = dd.DateField(_("Situation on"), blank=True)
    text_body = dd.RichTextField(_("Text body"), blank=True, format='html')
    state = ReminderStates.field(default=ReminderStates.as_callable('draft'))
    degree = ReminderDegrees.field(
        default=ReminderDegrees.as_callable('first'))
    remark = dd.CharField(_("Remark"), max_length=240, blank=True)

    # def on_create(self, ar):
    #     super(Reminder, self).on_create(ar)
    #     self.date_issued = dd.today()

    def __str__(self):
        return "{} ({} {})".format(
            dd.fds(self.date_issued), self.state, self.degree)

    def get_print_language(self):
        return self.enrolment.pupil.language

    def full_clean(self):
        #raise Exception("20180124")
        if self.date_issued is None:
            Event = rt.models.cal.Event
            flt = gfk2lookup(Event.owner, self.enrolment.course)
            qs = Event.objects.filter(**flt).order_by('-start_date')
            qs = qs.filter(state__in=EntryStates.filter(fixed=True))
            ce = qs.first()
            if ce is None:
                self.date_issued = dd.today()
            else:
                self.date_issued = ce.start_date
        super(Reminder, self).full_clean()
        
    
# class EnrolmentChecker(Checker):
#     verbose_name = _("Check for unsufficient presences")
#     model = Enrolment
#     messages = dict(
#         msg_absent=_("More than 2 times absent."),
#         msg_missed=_("Missed more than 10% of meetings."),
#     )
    
#     def get_checkdata_problems(self, obj, fix=False):
#         Guest = rt.models.cal.Guest
#         GuestStates = rt.models.cal.GuestStates
#         Event = rt.models.cal.Event
#         Reminder = rt.models.courses.Reminder
#         EnrolmentStates = rt.models.courses.EnrolmentStates
#         EntryStates = rt.models.cal.EntryStates

#         if obj.state != EnrolmentStates.confirmed:
#             return

#         qs = Reminder.objects.filter(enrolment=obj)
#         qs = qs.exclude(state=ReminderStates.cancelled)
#         rdate = qs.order_by('-date_issued').first()
#         if rdate is not None:
#             rdate = rdate.date_issued
#         eflt = gfk2lookup(Event.owner, obj.course)
#         gflt = { 'event__'+k: v for k, v in eflt.items() }
#         qs = Guest.objects.filter(partner=obj.pupil, **gflt)
#         # qs = qs.filter(**gfk2lookup(Guest.course, obj.course))
#         if rdate:
#             qs = qs.filter(event__start_date__gt=rdate)
#         if obj.request_date:
#             qs = qs.filter(event__start_date__gte=obj.request_date)
            
#         absent = qs.filter(state=GuestStates.missing).count()
#         if absent > 2:
#             yield (False, self.messages['msg_absent'])
#             return
#         # events = Event.objects.filter(**eflt)
#         # events = events.filter(state=EntryStates.took_place)
#         # ecount = events.count()
#         ecount = obj.course.max_events or 0
#         if ecount > 9:
#             excused = qs.filter(state=GuestStates.excused).count()
#             missing = absent + excused
#             max_missing = ecount / 10 - 1
#             if missing > max_missing:
#                 yield (False, self.messages['msg_missed'])
#                 return
    
#     def get_responsible_user(self, obj):
#         if obj.pupil and obj.pupil.user:
#             return obj.pupil.user
#         return super(EnrolmentChecker, self).get_responsible_user(obj)

# EnrolmentChecker.activate()
    
@dd.schedule_daily()
def update_missing_rates():
    for obj in rt.models.courses.Enrolment.objects.all():
        obj.update_missing_rate()
