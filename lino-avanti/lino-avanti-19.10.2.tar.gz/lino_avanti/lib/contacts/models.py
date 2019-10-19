# Copyright 2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""
The :xfile:`models.py` module for this plugin.

"""


from django.utils.translation import ugettext_lazy as _

from lino_xl.lib.contacts.models import *

#from lino_xl.lib.beid.mixins import BeIdCardHolder


# class Person(Person, BeIdCardHolder):

#     class Meta(Person.Meta):
#         app_label = 'contacts'
#         abstract = dd.is_abstract_model(__name__, 'Person')

#     validate_national_id = True        


class PartnerDetail(PartnerDetail):

    main = 'general address more'

    general = dd.Panel("""
    overview:30 contact_box:30 lists.MembersByPartner:20
    bottom_box
    """, label=_("General"))

    address = dd.Panel("""
    address_box
    #sepa.AccountsByPartner
    """, label=_("Address"))

    more = dd.Panel("""
    id language client_contact_type
    addr1 url
    #courses.CoursesByCompany
    excerpts.ExcerptsByOwner cal.GuestsByPartner
    """, label=_("More"))

    bottom_box = """
    remarks:50 checkdata.ProblemsByOwner:30
    """

    # A layout for use in Belgium
    address_box = """
    name
    street:25 #street_no street_box
    addr2
    country zip_code:10 city
    """

    contact_box = """
    #mti_navigator
    email
    phone
    #fax
    gsm
    """


class CompanyDetail(CompanyDetail, PartnerDetail):


    main = 'general address more'

    general = dd.Panel("""
    overview:30 contact_box:30 lists.MembersByPartner:20
    bottom_box
    """, label=_("General"))

    address = dd.Panel("""
    address_box
    contacts.RolesByCompany
    """, label=_("Address"))

    more = dd.Panel("""
    id language type client_contact_type
    addr1 url
    # notes.NotesByCompany
    clients.ClientContactsByCompany
    checkdata.ProblemsByOwner 
    """, label=_("More"))

    address_box = """
    prefix name
    street:25 #street_no street_box
    addr2
    country zip_code:10 city
    """    

    contact_box = dd.Panel("""
    #mti_navigator
    email:40
    phone
    gsm
    fax
    """)  # ,label = _("Contact"))

    bottom_box = """
    remarks:50
    """


class PersonDetail(PersonDetail, PartnerDetail):

    main = 'general address more'

    general = dd.Panel("""
    overview:30 contact_box:30 lists.MembersByPartner:20
    bottom_box
    """, label=_("General"))

    address = dd.Panel("""
    address_box
    contacts.RolesByPerson
    """, label=_("Address"))

    more = dd.Panel("""
    id language url
    addr1 addr2
    # notes.NotesByPerson
    """, label=_("More"))

    address_box = """
    last_name first_name:15 #title:10 gender
    street:25 #street_no street_box
    country zip_code:10 city
    birth_date age:10
    """

    # personal = 'national_id card_number'
   
    bottom_box = """
    remarks:50 checkdata.ProblemsByOwner:30
    """

Persons.set_detail_layout(PersonDetail())
Companies.set_detail_layout(CompanyDetail())
# Partners.set_detail_layout(PartnerDetail())


# Lino Avanti uses the `overview` field only in detail forms, and we
# don't want it to have a label "Description":
dd.update_field(Partner, 'overview', verbose_name=None)    

