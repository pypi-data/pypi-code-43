import django.core.exceptions
from django.core.exceptions import ObjectDoesNotExist
"""
The purpose of this module is to simplify the ability to import the 'ObjectDoesNotExist' exception without introducing a circular dependency
between savory_pie.fields and savory_pie.django.fields.
"""