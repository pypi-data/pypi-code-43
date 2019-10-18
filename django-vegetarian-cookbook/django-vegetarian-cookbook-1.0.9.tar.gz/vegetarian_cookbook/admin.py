"""
Django Vegetarian Cookbook, Copyright © 2018 Sergey Panasenko.
Contacts: <sergey.panasenko@gmail.com>
License: https://opensource.org/licenses/AGPL-3.0
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from imagekit.admin import AdminThumbnail

from .models import Nutrient, Unit, Ingredient, IngredientUnit
from .models import IngredientNutritionalValue, Category, Tag, Recipe
from .models import RecipeIngredient, RecipeImage
from .forms import IngredientForm, RecipeForm, RecipeIngredientInlineForm

admin.site.site_header = _('My recipes')
LINK_HTML = '<a href="{}" target="_blank">{}</a>'


@admin.register(Nutrient)
class NutrientAdmin(admin.ModelAdmin):
    """ Register Nutrient Model in Admin """
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """ Register Category Model in Admin """
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')
    admin_thumbnail.short_description = _('Thumbnail')
    list_display = ('admin_thumbnail', 'name')
    list_display_links = ['name']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    """ Register Category Model in Admin """


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """ Register Tag Model in Admin """
    readonly_fields = ('counter',)
    list_display = ('name', 'counter')
    search_fields = ['name']

    def get_ordering(self, request):
        return ['name']


class IngredientUnitInline(admin.TabularInline):
    """ Inline Unit for Ingredient """
    model = IngredientUnit
    extra = 0


class IngredientNutritionalValueInline(admin.TabularInline):
    """ Inline NutritionalValue for Ingredient """
    model = IngredientNutritionalValue
    autocomplete_fields = ('nutrient',)
    extra = 0


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """ Register Ingredient Model in Admin """
    form = IngredientForm
    list_display = ('admin_thumbnail', 'name', 'generate_url', 'energy',
                    'protein', 'fat', 'carbohydrate')
    list_display_links = ['name']
    search_fields = ['name']
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')
    admin_thumbnail.short_description = _('Thumbnail')
    fields = ('generate_url', 'name', 'image', 'description',
              'energy', 'protein', 'fat', 'carbohydrate')
    readonly_fields = ('generate_url',)
    inlines = [
        IngredientUnitInline,
        IngredientNutritionalValueInline
    ]

    def get_ordering(self, request):
        return ['name']

    def generate_url(self, obj):
        """ generate link to ingridient """
        if not obj.name:
            return '???'
        return format_html(LINK_HTML,
                           reverse('recipes_ingredient', args=(obj.name,)),
                           obj.name)
    generate_url.short_description = _('Url')


class RecipeIngredientInline(admin.TabularInline):
    """ Inline Ingredient for Recipe """
    model = RecipeIngredient
    form = RecipeIngredientInlineForm
    fields = ('ingredient', 'weight', 'or_col', 'quantity', 'unit', 'roughly')
    readonly_fields = ('or_col',)
    autocomplete_fields = ('ingredient',)

    def or_col(self, obj):
        """ add OR column """
        return _('OR')
    or_col.short_description = ''


class RecipeImageInline(admin.TabularInline):
    """ Inline Image for Recipe """
    model = RecipeImage
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """ Register Recipe Model in Admin """
    form = RecipeForm
    list_display = ('admin_thumbnail', 'title', 'status_url', 'fullness',
                    'category', 'recipe_tags', 'recipe_ingredients')
    list_display_links = ['title']
    search_fields = ['title']
    autocomplete_fields = ('tags',)
    list_filter = ['category', 'tags', 'recipeingredient__ingredient__name']
    exclude = ('url', 'energy', 'protein', 'fat', 'carbohydrate', 'weight')
    fieldsets = (
        (None, {
            'fields': ('title', ('status', 'generate_url'),
                       ('complexity', 'category'),
                       'time', 'image', 'tags', 'description')
        }),
        ('Manual setting', {
            'classes': ('collapse', ),
            'fields': ('manually_weight', 'manually_energy',
                       'manually_protein', 'manually_fat',
                       'manually_carbohydrate'),
        }),
    )
    inlines = [
        RecipeIngredientInline,
        RecipeImageInline
    ]
    readonly_fields = ('generate_url', 'status_url',)
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')
    admin_thumbnail.short_description = _('Thumbnail')

    def save_formset(self, request, form, formset, change):
        if formset.model == RecipeIngredient:
            for _form in formset.forms:
                instance = _form.instance
                if instance.quantity > 0 and instance.unit:
                    ingredient_unit = IngredientUnit.objects.get(
                        unit=instance.unit,
                        ingredient=instance.ingredient)
                    instance.weight = int(instance.quantity *
                                          ingredient_unit.ratio)
        if formset.model == RecipeImage:
            for _form in formset.forms:
                instance = _form.instance
                if instance.id and not instance.image:
                    form.instance.delete()
        formset.save()

    def save_model(self, request, obj, form, change):
        obj.fix_url()
        if not obj.weight:
            obj.weight = 0
        super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        obj.calculate()
        obj.save()
        obj.count_tags()
        return super(RecipeAdmin, self).response_add(request, obj,
                                                     post_url_continue)

    def response_change(self, request, obj):
        obj.calculate()
        obj.save()
        obj.count_tags()
        return super(RecipeAdmin, self).response_change(request, obj)

    def delete_model(self, request, obj):
        obj.status = u'i'
        obj.save()
        obj.count_tags()
        super(RecipeAdmin, self).delete_model(request, obj)

    def generate_url(self, obj):
        """ return link to recipe """
        if not obj.url:
            return '???'
        url = reverse('recipes_recipe', args=(obj.url, ))
        return format_html(LINK_HTML, url, url)
    generate_url.short_description = _('Url')

    def status_url(self, obj):
        """ return link to recipe with recipe status """
        if not obj.url:
            return obj.get_status_display()
        return format_html(LINK_HTML,
                           reverse('recipes_recipe', args=(obj.url,)),
                           obj.get_status_display())
    status_url.short_description = _('status')
