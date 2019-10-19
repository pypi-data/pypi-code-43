# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""The models for this plugin.
"""

from __future__ import unicode_literals

from lino_xl.lib.households.models import *

from django.utils.translation import ugettext_lazy as _


class Member(Member):

    class Meta(Member.Meta):
        abstract = dd.is_abstract_model(__name__, 'Member')

    nationality = dd.ForeignKey(
        'countries.Country',
        verbose_name=_("Nationality"), blank=True, null=True)
    school = models.CharField(_("School"), max_length=200, blank=True)

MembersByHousehold.column_names = \
    "age:10 role person \
    first_name last_name gender birth_date nationality school *"
SiblingsByPerson.column_names = "age:10 role person \
    first_name last_name gender birth_date nationality school *"
