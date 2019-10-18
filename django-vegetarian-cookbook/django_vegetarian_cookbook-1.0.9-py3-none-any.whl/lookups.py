# Django Vegetarian Cookbook, Copyright © 2018 Sergey Panasenko.
# Contacts: <sergey.panasenko@gmail.com>
# License: https://opensource.org/licenses/AGPL-3.0

from django.utils.html import escape
from django.db.models import Q
from ajax_select import LookupChannel
from .models import Tag, Ingredient, Nutrient, Unit, IngredientUnit
import ajax_select

@ajax_select.register('Nutrient')
class NutrientLookup(LookupChannel):
    model = Nutrient
    def get_query(self, q, request):
        q_capitalized = q.capitalize();
        return Nutrient.objects.filter(Q(name__icontains=q) | \
                Q(name__icontains=q_capitalized)).order_by('name')

@ajax_select.register('Tag')
class TagLookup(LookupChannel):
    model = Tag
    def can_add(self, user, model):
        return False
    def get_query(self, q, request):
        q_capitalized = q.capitalize();
        return Tag.objects.filter(Q(name__icontains=q) | \
                Q(name__icontains=q_capitalized)).order_by('name')

@ajax_select.register('Ingredient')
class IngredientLookup(LookupChannel):
    model = Ingredient
    def get_query(self, q, request):
        q_capitalized = q.capitalize();
        return Ingredient.objects.filter(Q(name__icontains=q) | \
                Q(name__icontains=q_capitalized)).order_by('name')

@ajax_select.register('IngredientUnit')
class IngredientUnitLookup(LookupChannel):
    model = IngredientUnit
    def get_query(self, q, request):
        return IngredientUnit.objects.filter().order_by('unit__name')
    def can_add(self, user, model):
        return False

