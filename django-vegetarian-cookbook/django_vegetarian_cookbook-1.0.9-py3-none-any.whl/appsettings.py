"""
Django Vegetarian Cookbook, Copyright © 2018 Sergey Panasenko.
Contacts: <sergey.panasenko@gmail.com>
License: https://opensource.org/licenses/AGPL-3.0
"""
from django.utils.translation import gettext as _
from django.conf import settings

RECIPES_IN_LIST = getattr(settings, 'RECIPES_IN_LIST', 6)
INGREDIENTS_IN_LIST = getattr(settings, 'INGREDIENTS_IN_LIST', 20)
RECIPES_IN_SEARCH = getattr(settings, 'RECIPES_IN_SEARCH', 20)
SEO_DESCRIPTION = getattr(settings, 'SEO_DESCRIPTION',
                          _('The best proven vegetarian recipes with '
                            'calculation of calories and nutrients.'))
SEO_KEYWORDS = getattr(settings, 'SEO_KEYWORDS',
                       _('recipe, culinary, cookbook, vegetarian food, vegan,'
                         'raw food, raw diet, vegetarianism, diet, '
                         'healthy food,'))
NPLURALS = getattr(settings, 'NPLURALS', 2)
PLURAL = getattr(settings, 'PLURAL', lambda n: 0 if n == 1 else 1)
