"""
Django Vegetarian Cookbook, Copyright © 2018 Sergey Panasenko.
Contacts: <sergey.panasenko@gmail.com>
License: https://opensource.org/licenses/AGPL-3.0
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class VegetarianCookbookConfig(AppConfig):
    """ config class for application """
    name = 'vegetarian_cookbook'
    verbose_name = _("Vegetarian Cookbook")
