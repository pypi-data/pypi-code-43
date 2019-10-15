# -*- coding: UTF-8 -*-
# Copyright 2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals

from lino_xl.lib.cv.models import *

from lino.api import _


class Study(Study):

    class Meta(Study.Meta):
        abstract = dd.is_abstract_model(__name__, 'Study')

    foreign_education_level = dd.ForeignKey(
        'cv.EducationLevel',
        verbose_name=_("Foreign education level"),
        related_name="studies_by_foreign_education_level",
        null=True, blank=True)

    recognized = models.BooleanField(_("Recognized in Belgium"), default=False)


class StudyDetail(StudyDetail):
    main = """
    person #start_date #end_date duration_text language
    type content education_level state #success
    foreign_education_level recognized
    school country city
    remarks
    """

StudiesByPerson.column_names = 'type content duration_text language school country state education_level foreign_education_level recognized remarks *'

StudiesByPerson.insert_layout = """
type content
duration_text language
"""

Experiences.detail_layout = """
person company country city
#sector #function title
status duration regime is_training
#start_date #end_date duration_text termination_reason
remarks
"""

ExperiencesByPerson.column_names = "company country duration_text function status termination_reason remarks *"

dd.update_field(Experience, 'company', verbose_name=_("Work area"))
