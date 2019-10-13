from django.db import models
from datetime import datetime, timedelta
import os
from django.utils.deconstruct import deconstructible
from common import common_helpers

from django.db.models import Q

SCHOOL_TYPE = [('Primary', 'Primary school'), ('Secondary', 'Secondary school'), ('All', 'All through 5-18 school')]
ACCOUNT_TYPE = [('Test', 'Test'), ('Demo', 'Demo'), ('Full', 'Full')]


class AuthorityManager(models.Manager):

    def get_all_authorities(self):
        return self.all().order_by('authority_name')

class Authority(models.Model):
    authority_name = models.CharField(max_length=100)
    objects = AuthorityManager()

    def __str__(self):
        return self.authority_name

def expiry_plus_one_year():
    return (datetime.today() + timedelta(days=365)).date()

def expiry_plus_28_days():
    return (datetime.today() + timedelta(days=28)).date()


def current_date_time():
    return datetime.today()

class SchoolManager(models.Manager):

    def new_school_account(self, school_name, authority, school_type):

        new_school_account = self.model(
            school_name=school_name,
            authority=authority,
            school_type=school_type
        )

        new_school_account.save()

        return new_school_account

    def get_all_schools(self):
        return self.all().order_by('school_name')

    def get_school(self, school_pk):

        return self.get(
            pk=school_pk
        )


    def update_stakeholder_surveys_visit(self, school):
        visit_time = datetime.today()
        school.stakeholder_surveys_last_visit = visit_time
        school.save()

    def update_self_evaluation_visit(self, school):
        visit_time = datetime.today()
        school.self_evaluation_last_visit = visit_time
        school.save()

    def update_improvement_plan_visit(self, school):
        visit_time = datetime.today()
        school.improvement_plan_last_visit = visit_time
        school.save()


    def school_postcode_exists(self, postcode):


        if postcode is not None:
            postcode = postcode.replace(' ', '').upper()

        return self.filter(
            postcode=postcode
        ).exists()



    def get_schools_by_postcode(self, postcode):

        if postcode is not None:
            postcode = postcode.replace(' ', '').upper()

        if self.school_postcode_exists(postcode):

            return self.filter(
                postcode=postcode
            )
        return None


def lower_case_no_spaces(text):
    text.replace(' ', '-')
    text = text.lower()
    return text

@deconstructible
class BadgeUploadPath(object):

    def __call__(self, instance, filename):
        school_name_as_filename = lower_case_no_spaces(instance.school_name)
        ext = filename.split('.')[-1]
        filename = str(instance.pk) + '-' + school_name_as_filename + '.' + ext

        path = "images/badges"
        return os.path.join(path, filename)


class School(models.Model):
    school_name = models.CharField(max_length=150, default='')
    school_type = models.CharField(max_length=150, choices=SCHOOL_TYPE, default='Primary')
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE, blank=True, null=True)
    active_account = models.BooleanField(default=True)
    account_expiry = models.DateField(default=expiry_plus_28_days, blank=True)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE, default='Full')
    postcode = models.CharField(max_length=8, default='', blank=True)
    is_departmental_school = models.BooleanField(default=False)
    school_badge = models.ImageField(upload_to=BadgeUploadPath(), null=True, blank=True)

    self_evaluation_last_visit = models.DateField(default=None, blank=True, null=True)
    stakeholder_surveys_last_visit = models.DateField(default=None, blank=True, null=True)
    improvement_plan_last_visit = models.DateField(default=None, blank=True, null=True)

    objects = SchoolManager()

    def __str__(self):
        return self.school_name



class FacultyManager(models.Manager):

    def get_faculty(self, pk):

        return self.get(
            pk=pk
        )

    # return faculties where owner is NULL (i.e. these are core Impact faculties)
    # or where owner is the current user's school
    def get_school_and_default_faculties(self, user):
        school_default_faculties = self.filter(
            Q(owner__isnull=True) |
            Q(owner=user.get_school()))
        return school_default_faculties

    # return faculties where ownereis the current user's school
    def get_school_faculties(self, user):
        return self.filter(owner=user.get_school()).order_by('faculty_name')

    def get_school_faculties_non_member(self, user):

        user_is_member = user.member_of_faculties.all()

        return self.filter(
            owner=user.get_school()
        ).exclude(id__in=user_is_member).order_by('faculty_name')


    def create_faculty(self, faculty_name, user):

        faculty = self.model(
            faculty_name=faculty_name,
            owner=user.get_school()
        )

        faculty.save()

        return faculty

    def update_faculty_name(self, faculty, faculty_name):

        faculty.faculty_name = faculty_name
        faculty.save()


    def delete(self, pk):
        faculty = self.get(pk=pk)
        faculty.delete()

    def get_school_as_faculty(self):
        return self.get(
            faculty_name='School',
            owner__isnull=True
        )

    def get_school_pk(self):

        return self.get(
            faculty_name = 'School'
        ).pk


class Faculty(models.Model):
    faculty_name = models.CharField(max_length=100, default='')
    owner = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True)

    objects = FacultyManager()

    def __str__(self):
        return self.faculty_name



