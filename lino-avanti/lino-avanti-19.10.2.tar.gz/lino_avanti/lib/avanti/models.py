# -*- coding: UTF-8 -*-
# Copyright 2017-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""The :xfile:`models.py` module for this plugin.

See :doc:`/specs/avanti/avanti`.

"""

from __future__ import unicode_literals
from builtins import str

from lino.api import dd, rt, _
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils.text import format_lazy

from lino.utils import join_elems
from etgen.html import E
from lino.utils.dates import daterange_text
# from lino.utils import ssin
from lino.mixins import Referrable
from lino.mixins.human import strip_name_prefix
from lino_xl.lib.beid.mixins import BeIdCardHolder
from lino.modlib.comments.mixins import Commentable
from lino.modlib.users.mixins import UserAuthored, My
from lino.modlib.dupable.mixins import Dupable
from lino.modlib.system.mixins import Lockable
from lino_xl.lib.courses.mixins import Enrollable

# from lino.modlib.notify.mixins import ChangeNotifier
# from lino_xl.lib.notes.choicelists import SpecialTypes
# from lino_xl.lib.coachings.mixins import Coachable
from lino_xl.lib.clients.mixins import ClientBase
# from lino_xl.lib.notes.mixins import Notable
from lino_xl.lib.cal.mixins import EventGenerator
from lino_xl.lib.cal.workflows import TaskStates
from lino_xl.lib.cv.mixins import BiographyOwner
# from lino.utils.mldbc.fields import BabelVirtualField

from lino.mixins import ObservedDateRange

from lino_xl.lib.clients.choicelists import ClientEvents, ClientStates



from .choicelists import TranslatorTypes, StartingReasons, ProfessionalStates

from .choicelists import OldEndingReasons

from lino.core.roles import Explorer
from .roles import ClientsNameUser, ClientsUser, ClientsStaff
from lino_xl.lib.cv.roles import CareerUser

contacts = dd.resolve_app('contacts')

# def cef_level_getter(lng):
#     def f(obj):
#         LanguageKnowledge = rt.models.cv.LanguageKnowledge
#         if obj._cef_levels is None:
#             obj._cef_levels = dict()
#             for lk in LanguageKnowledge.objects.filter(person=obj):
#                 obj._cef_levels[lk.language.iso2] = lk.obj._cef_levels
#         return obj._cef_levels.get(lng.django_code)
#     return f

from lino.utils.mldbc.mixins import BabelDesignated

class Category(BabelDesignated):
    
    class Meta:
        app_label = 'avanti'
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        abstract = dd.is_abstract_model(__name__, 'Category')

class Categories(dd.Table):
    model = 'avanti.Category'
    required_roles = dd.login_required(ClientsStaff)

class EndingReason(BabelDesignated):
    
    class Meta:
        app_label = 'avanti'
        verbose_name = _("Ending reason")
        verbose_name_plural = _("Ending reasons")
        abstract = dd.is_abstract_model(__name__, 'Category')

        
class EndingReasons(dd.Table):
    model = 'avanti.EndingReason'
    required_roles = dd.login_required(ClientsStaff)


@dd.python_2_unicode_compatible
class Client(contacts.Person, BeIdCardHolder, UserAuthored,
             ClientBase, BiographyOwner, Referrable, Dupable,
             Lockable,
             Commentable, EventGenerator, Enrollable):
    class Meta:
        app_label = 'avanti'
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        abstract = dd.is_abstract_model(__name__, 'Client')
        #~ ordering = ['last_name','first_name']

    quick_search_fields = "name phone gsm ref"

    is_obsolete = False  # coachings checker

    beid_readonly_fields = set()
    manager_roles_required = dd.login_required(ClientsUser)
    validate_national_id = True
    _cef_levels = None
    _mother_tongues = None

    # in_belgium_since = models.DateField(
    #     _("Lives in Belgium since"), blank=True, null=True)
    
    in_belgium_since = dd.IncompleteDateField(
        _("Lives in Belgium since"), blank=True, null=True)
    
    in_region_since = dd.IncompleteDateField(
        _("Lives in region since"), blank=True, null=True)
    
    starting_reason = StartingReasons.field(blank=True)
    old_ending_reason = OldEndingReasons.field(blank=True)
    ending_reason = dd.ForeignKey(
        'avanti.EndingReason', blank=True, null=True)
    professional_state = ProfessionalStates.field(blank=True)
    category = dd.ForeignKey(
        'avanti.Category', blank=True, null=True)
    
    translator_type = TranslatorTypes.field(blank=True)
    translator_notes = dd.RichTextField(
        _("Translator"), blank=True, format='plain')
    # translator = dd.ForeignKey(
    #     "avanti.Translator",
    #     blank=True, null=True)

    unemployed_since = models.DateField(
        _("Unemployed since"), blank=True, null=True,
        help_text=_("Since when the client has not been employed "
                    "in any regular job."))
    seeking_since = models.DateField(
        _("Seeking work since"), blank=True, null=True,
        help_text=_("Since when the client is seeking for a job."))
    needs_work_permit = models.BooleanField(
        _("Needs work permit"), default=False)
    work_permit_suspended_until = models.DateField(
        blank=True, null=True, verbose_name=_("suspended until"))
    has_contact_pcsw = models.BooleanField(
        _("Has contact to PCSW"), default=False)
    has_contact_work_office = models.BooleanField(
        _("Has contact to work office"), default=False)

    declared_name = models.BooleanField(_("Declared name"), default=False)

    # is_seeking = models.BooleanField(_("is seeking work"), default=False)
    # removed in chatelet, maybe soon also in Eupen (replaced by seeking_since)

    unavailable_until = models.DateField(
        blank=True, null=True, verbose_name=_("Unavailable until"))
    unavailable_why = models.CharField(
        _("Reason"), max_length=100,
        blank=True)

    family_notes = models.TextField(
        _("Family situation"), blank=True, null=True)
    
    residence_notes = models.TextField(
        _("Residential situation"), blank=True, null=True)
    
    health_notes = models.TextField(
        _("Health situation"), blank=True, null=True)
    
    financial_notes = models.TextField(
        _("Financial situation"), blank=True, null=True)
    
    integration_notes = models.TextField(
        _("Integration notes"), blank=True, null=True)
    
    availability = models.TextField(
        _("Availability"), blank=True, null=True)

    needed_course = dd.ForeignKey(
        'courses.Line', verbose_name=_("Needed course"),
        blank=True, null=True)
    
    # obstacles = models.TextField(
    #     _("Other obstacles"), blank=True, null=True)
    # skills = models.TextField(
    #     _("Other skills"), blank=True, null=True)

    # client_state = ClientStates.field(
    #     default=ClientStates.newcomer.as_callable)

    event_policy = dd.ForeignKey(
        'cal.EventPolicy', blank=True, null=True)
    
    language_notes = dd.RichTextField(
        _("Language notes"), blank=True, format='plain')
    
    remarks = dd.RichTextField(
        _("Remarks"), blank=True, format='plain')
    
    reason_of_stay = models.CharField(
        _("Reason of stay"), max_length=200, blank=True)

    nationality2 = dd.ForeignKey('countries.Country',
                                blank=True, null=True,
                                related_name='by_nationality2',
                                verbose_name=format_lazy(u"{}{}",
                                    _("Nationality"), " (2)"))
    def __str__(self):
        return "%s %s (%s)" % (
            self.last_name.upper(), self.first_name, self.pk)

    def get_choices_text(self, ar, actor, field):
        if ar:
            u = ar.subst_user or ar.user
            if u.user_type.has_required_roles(
                    [ClientsNameUser]):
                return str(self)
        # 20180209 : not even the first name
        # return _("{} ({}) from {}").format(
        #     self.first_name, self.pk, self.city)
        return _("({}) from {}").format( self.pk, self.city)
        # return "{} {}".format(self._meta.verbose_name, self.pk)

    @dd.displayfield(_("Name"))
    def name_column(self, ar):
        return str(self)

    @dd.displayfield(_("Municipality"))
    def municipality(self, ar):
        pl = self.city
        mt = dd.plugins.avanti.municipality_type
        while pl and pl.parent_id and pl.type and pl.type.value > mt:
            pl = pl.parent
        return str(pl)

    def get_overview_elems(self, ar):
        elems = super(Client, self).get_overview_elems(ar)
        # elems.append(E.br())
        elems.append(ar.get_data_value(self, 'eid_info'))
        notes = []
        for obj in rt.models.cal.Task.objects.filter(
                project=self, state=TaskStates.important):
            notes.append(E.b(ar.obj2html(obj, obj.summary)))
        if len(notes):
            notes = join_elems(notes, " / ")
            elems.append(E.p(*notes, **{'class':"lino-info-yellow"}))
        return elems

    def update_owned_instance(self, owned):
        owned.project = self
        super(Client, self).update_owned_instance(owned)

    # def full_clean(self, *args, **kw):
    #     if self.national_id:
    #         ssin.ssin_validator(self.national_id)
    #     super(Client, self).full_clean(*args, **kw)

    def properties_list(self, *prop_ids):
        """Yields a list of the :class:`PersonProperty
        <lino_welfare.modlib.cv.models.PersonProperty>` properties of
        this person in the specified order.  If this person has no
        entry for a requested :class:`Property`, it is simply skipped.
        Used in :xfile:`cv.odt`.  `

        """
        return rt.models.cv.properties_list(self, *prop_ids)

    def get_events_user(self):
        return self.get_primary_coach()
        
    def update_cal_rset(self):
        return self.event_policy
    
    def update_cal_event_type(self):
        if self.event_policy is not None:
            return self.event_policy.event_type
        
    def update_cal_from(self, ar):
        return dd.today()
        # pc = self.get_primary_coaching()
        # if pc:
        #     return pc.start_date
    
    def update_cal_until(self):
        return dd.today(365)
        # pc = self.get_primary_coaching()
        # if pc:
        #     return pc.end_date


    def get_dupable_words(self, s):
        s = strip_name_prefix(s)
        return super(Client, self).get_dupable_words(s)

    def find_similar_instances(self, limit=None, **kwargs):
        """Overrides
        :meth:`lino.modlib.dupable.mixins.Dupable.find_similar_instances`,
        adding some additional rules.

        """
        # kwargs.update(is_obsolete=False, national_id__isnull=True)
        qs = super(Client, self).find_similar_instances(None, **kwargs)
        if self.national_id:
            qs = qs.filter(national_id__isnull=True)
        # else:
        #     qs = qs.filter(national_id__isnull=False)
        if self.birth_date:
            qs = qs.filter(Q(birth_date='') | Q(birth_date=self.birth_date))

        last_name_words = set(self.get_dupable_words(self.last_name))

        found = 0
        for other in qs:
            found += 1
            if limit is not None and found > limit:
                return
            ok = False
            for w in other.get_dupable_words(other.last_name):
                if w in last_name_words:
                    ok = True
                    break
            if ok:
                yield other



        

dd.update_field(Client, 'user', verbose_name=_("Primary coach"))
dd.update_field(Client, 'ref', verbose_name=_("Legacy file number"))
    

class ClientDetail(dd.DetailLayout):

    main = "general person contact courses_tab family \
    notes career trends #polls #courses misc db_tab"

    general = dd.Panel("""
    general1:30 general2:40 image:15
    
    cal.EntriesByProject cal.GuestsByPartner
    """, label=_("General"))

    general1 = """
    overview
    """
    general2 = """
    id:10 national_id:15 ref #lock_or_unlock:10
    birth_date age:10 gender:10
    starting_reason professional_state
    reason_of_stay category
    client_state user #primary_coach
    event_policy ending_reason 
    # workflow_buttons 
    """

    contact = dd.Panel("""
    address general3
    ResidencesByPerson
    """, label=_("Residence"))

    address = """
    country city zip_code:10
    addr1
    street:25 street_no #street_box
    addr2
    """

    general3 = """
    email
    phone
    fax
    gsm
    """

    person = dd.Panel("""
    first_name middle_name last_name #declared_name
    nationality:15 nationality2:15 birth_country birth_place in_belgium_since in_region_since
    card_type #card_number card_issuer card_valid_from card_valid_until
    needs_work_permit has_contact_pcsw has_contact_work_office
    clients.ContactsByClient uploads.UploadsByClient excerpts.ExcerptsByProject:30
    """, label=_("Person"))

    courses_tab = dd.Panel("""
    translator_left:15 translator_notes:20 cv.LanguageKnowledgesByPerson:20
    language_notes:20 courses.EnrolmentsByPupil:60 #courses_right:20
    """, label=_("Courses"))

    translator_left = """
    language 
    translator_type
    # mother_tongues
    """
    courses_right = """
    needed_course
    availability:20
    """
    # translator_right = """
    # language_knowledge
    # # cef_level_de
    # # cef_level_fr
    # # cef_level_en 
    # """

    family = dd.Panel("""
    households.MembersByPerson:20
    #humanlinks.LinksByHuman:30
    households.SiblingsByPerson
    """, label=_("Family"), required_roles=dd.login_required(CareerUser))

    notes = dd.Panel("""
    comments.CommentsByRFC notes_right
    """, label=_("Notes"), required_roles=dd.login_required(CareerUser))
    
    notes_right = """
    cal.TasksByProject
    courses.RemindersByPupil
    """

    # courses = dd.Panel("""
    # courses.EnrolmentsByPupil
    # """, label = _("Courses"))

    trends = dd.Panel("""
    trends.EventsBySubject polls.ResponsesByPartner
    """, label = _("Trends"))

    # polls = dd.Panel("""
    # polls.ResponsesByPartner
    # """, label = _("Polls"))

    misc = dd.Panel("""
    # unavailable_until:15 unavailable_why:30
    financial_notes health_notes integration_notes
    remarks family_notes residence_notes
    """, label=_("Miscellaneous"), required_roles=dd.login_required(
        CareerUser))

    db_tab = dd.Panel("""
    changes.ChangesByMaster
    checkdata.ProblemsByOwner:30 dupable.SimilarObjects:30
    """, label = _("Database"))

    career = dd.Panel("""
    # unemployed_since seeking_since work_permit_suspended_until
    cv.StudiesByPerson
    # cv.TrainingsByPerson
    cv.ExperiencesByPerson:40
    """, label=_("Career"))

    # calendar = dd.Panel("""
    # cal.GuestsByPartner
    # """, label=_("Calendar"))

    # competences = dd.Panel("""
    # skills
    # obstacles
    # """, label=_("Competences"))


# Client.hide_elements('street_prefix', 'addr2')


class Clients(contacts.Persons):
    model = 'avanti.Client'
    params_panel_hidden = True
    required_roles = dd.login_required(ClientsUser)

    # insert_layout = dd.InsertLayout("""
    # first_name last_name
    # national_id
    # gender language
    # """, window_size=(60, 'auto'))

    column_names = "name_column:20 client_state national_id:10 \
    gsm:10 address_column age:10 email phone:10 id language:10 *"

    detail_layout = ClientDetail()

    parameters = ObservedDateRange(
        nationality=dd.ForeignKey(
            'countries.Country', blank=True, null=True,
            verbose_name=_("Nationality")))
        # observed_event=ClientEvents.field(blank=True)
    params_layout = """
    aged_from aged_to gender nationality client_state user
    start_date end_date #observed_event course enrolment_state client_contact_type client_contact_company
    """

    @classmethod
    def get_request_queryset(self, ar):
        """This converts the values of the different parameter panel fields to
        the query filter.


        """
        qs = super(Clients, self).get_request_queryset(ar)

        pv = ar.param_values
        # period = [pv.start_date, pv.end_date]
        # if period[0] is None:
        #     period[0] = period[1] or dd.today()
        # if period[1] is None:
        #     period[1] = period[0]

        ce = pv.observed_event
        if ce:
            qs = ce.add_filter(qs, pv)

        # if ce is None:
        #     pass
        # elif ce == ClientEvents.active:
        #     pass
        # elif ce == ClientEvents.isip:
        #     flt = has_contracts_filter('isip_contract_set_by_client', period)
        #     qs = qs.filter(flt).distinct()
        # elif ce == ClientEvents.jobs:
        #     flt = has_contracts_filter('jobs_contract_set_by_client', period)
        #     qs = qs.filter(flt).distinct()
        # elif dd.is_installed('immersion') and ce == ClientEvents.immersion:
        #     flt = has_contracts_filter(
        #         'immersion_contract_set_by_client', period)
        #     qs = qs.filter(flt).distinct()

        # elif ce == ClientEvents.available:
        #     # Build a condition "has some ISIP or some jobs.Contract
        #     # or some immersion.Contract" and then `exclude` it.
        #     flt = has_contracts_filter('isip_contract_set_by_client', period)
        #     flt |= has_contracts_filter('jobs_contract_set_by_client', period)
        #     if dd.is_installed('immersion'):
        #         flt |= has_contracts_filter(
        #             'immersion_contract_set_by_client', period)
        #     qs = qs.exclude(flt).distinct()


        if pv.nationality:
            qs = qs.filter(
                models.Q(nationality=pv.nationality)|
                models.Q(nationality2=pv.nationality))

        # print(20150305, qs.query)

        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Clients, self).get_title_tags(ar):
            yield t
        pv = ar.param_values

        # if pv.observed_event:
        #     yield str(pv.observed_event)

        if pv.start_date or pv.end_date:
            yield daterange_text(
                pv.start_date, pv.end_date)

    # @classmethod
    # def apply_cell_format(self, ar, row, col, recno, td):
    #     if row.client_state == ClientStates.newcomer:
    #         td.attrib.update(bgcolor="green")

    @classmethod
    def get_row_classes(cls, obj, ar):
        # if obj.client_state == ClientStates.newcomer:
        #     yield 'green'
        if obj.client_state in (ClientStates.refused, ClientStates.former):
            yield 'yellow'
        #~ if not obj.has_valid_card_data():
            #~ return 'red'


class AllClients(Clients):
    auto_fit_column_widths = False
    column_names = "client_state \
    starting_reason ending_reason \
    city municipality country zip_code nationality \
    #birth_date age:10 gender \
    birth_country #birth_place \
    in_belgium_since needs_work_permit \
    translator_type \
    mother_tongues cef_level_de cef_level_fr cef_level_en \
    user event_policy"
    detail_layout = None
    required_roles = dd.login_required(Explorer)



class ClientsByNationality(Clients):
    master_key = 'nationality'
    order_by = "city name".split()
    column_names = "city street street_no street_box addr2 name_column country language *"


class MyClients(My, Clients):
    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyClients, self).param_defaults(ar, **kw)
        kw.update(client_state='')
        return kw



# class ClientsByTranslator(Clients):
#     master_key = 'translator'

from lino_xl.lib.countries.mixins import CountryCity
from lino_xl.lib.cv.mixins import PersonHistoryEntry, HistoryByPerson

    
class Residence(PersonHistoryEntry, CountryCity):

    allow_cascaded_delete = ['person']

    class Meta:
        app_label = 'avanti'
        verbose_name = _("Residence")
        verbose_name_plural = _("Residences")

    reason = models.CharField(_("Reason"), max_length=200, blank=True)



class Residences(dd.Table):
    model = 'avanti.Residence'
    
class ResidencesByPerson(HistoryByPerson, Residences):
    label = _("Former residences")
    column_names = 'country city duration_text reason *'
    auto_fit_column_widths = True


# @dd.receiver(dd.pre_analyze)
# def inject_cef_level_fields(sender, **kw):
#     for lng in settings.SITE.languages:
#         fld = dd.VirtualField(
#             CefLevel.field(
#                 verbose_name=lng.name, blank=True), cef_level_getter(lng))
#         dd.inject_field(
#             'avanti.Client', 'cef_level_'+lng.prefix, fld)

#     def fc(**kwargs):
#         return (**kwargs)
    

from lino.api import _, pgettext
from lino_xl.lib.clients.choicelists import ClientStates
ClientStates.default_value = 'coached'
ClientStates.clear()
add = ClientStates.add_item
add('05', _("Incoming"), 'incoming')
add('07', _("Informed"), 'informed')
add('10', _("Newcomer"), 'newcomer')
add('20', pgettext("client state", "Registered"), 'coached')
add('25', _("Inactive"), 'inactive')
add('30', _("Ended"), 'former')
add('40', _("Abandoned"), 'refused')

# alias
# ClientStates.coached = ClientStates.newcomer


# @dd.receiver(dd.pre_analyze)
# def add_merge_action(sender, **kw):
#     apps = sender.modules
#     for m in (apps.avanti.Client, apps.contacts.Person,
#               apps.contacts.Company):
#         m.define_action(merge_row=dd.MergeAction(m))

