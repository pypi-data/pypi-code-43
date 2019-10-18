"""
Django Vegetarian Cookbook, Copyright © 2018 Sergey Panasenko.
Contacts: <sergey.panasenko@gmail.com>
License: https://opensource.org/licenses/AGPL-3.0
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from ajaximage.fields import AjaxImageField
from .translit import transliterate


class Nutrient(models.Model):
    """ Model of ingredient nutrient """
    name = models.CharField(max_length=255, verbose_name=_('tag name'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('nutrient')
        verbose_name_plural = _('nutrients')


class Unit(models.Model):
    """ Model of meashure unit """
    name = models.CharField(max_length=250, verbose_name=_('unit name'),
                            help_text=_("Example: cup"))
    plural = models.CharField(max_length=250, blank=True,
                              verbose_name=_('plural form'),
                              help_text=_("Example: cups (comma separated "
                                          "if language has more"
                                          " 2 plural forms)"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('unit')
        verbose_name_plural = _('units')


class Ingredient(models.Model):
    """ Model of ingredient """
    name = models.CharField(max_length=250, verbose_name=_('ingredient name'))
    image = models.ImageField(upload_to='images', blank=True,
                              verbose_name=_('image'))
    description = models.TextField(blank=True, verbose_name=_('description'))
    energy = models.DecimalField(max_digits=7, decimal_places=3, null=True,
                                 blank=True, verbose_name=_('energy'))
    protein = models.DecimalField(max_digits=7, decimal_places=3, null=True,
                                  blank=True, verbose_name=_('protein'))
    fat = models.DecimalField(max_digits=7, decimal_places=3, null=True,
                              blank=True, verbose_name=_('fat'))
    carbohydrate = models.DecimalField(max_digits=7, decimal_places=3,
                                       null=True, blank=True,
                                       verbose_name=_('carbohydrate'))
    thumbnail = ImageSpecField(source='image',
                               processors=[ResizeToFill(400, 300)],
                               format='JPEG', options={'quality': 90})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('ingredient')
        verbose_name_plural = _('ingredients')


class IngredientUnit(models.Model):
    """ Model of units used for ingredient """
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT,
                                   verbose_name=_('ingredient'))
    unit = models.ForeignKey(Unit, default=1, on_delete=models.PROTECT,
                             verbose_name=_('unit'))
    ratio = models.DecimalField(default=1, max_digits=10, decimal_places=4,
                                verbose_name=_('ratio'))

    def __str__(self):
        return self.ingredient.name + '/' + self.unit.name

    class Meta:
        verbose_name = _('additional unit')
        verbose_name_plural = _('additional units')


class IngredientNutritionalValue(models.Model):
    """ Model of nutritional value of ingredient """
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT,
                                   verbose_name=_('ingredient'))
    nutrient = models.ForeignKey(Nutrient, on_delete=models.CASCADE,
                                 verbose_name=_('nutrient'))
    value = models.DecimalField(default=1, max_digits=10, decimal_places=3,
                                verbose_name=_('value'))
    unit = models.ForeignKey(Unit, default=1, on_delete=models.PROTECT,
                             verbose_name=_('unit'))

    def __str__(self):
        return self.ingredient.name + '/' + self.nutrient.name

    class Meta:
        verbose_name = _('nutrient')
        verbose_name_plural = _('nutrients')


class Category(models.Model):
    """ Model of recipe category """
    name = models.CharField(max_length=120, verbose_name=_('categoty name'))
    image = models.ImageField(null=True, blank=True, upload_to='images',
                              verbose_name=_('image'))
    thumbnail = ImageSpecField(source='image',
                               processors=[ResizeToFill(64, 64)],
                               format='png', options={'quality': 90})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')


class Tag(models.Model):
    """ Model of recipe tags """
    name = models.CharField(max_length=120, verbose_name=_('tag name'))
    counter = models.IntegerField(default=0, verbose_name=_('counter'))

    def __str__(self):
        return self.name

    def weight(self):
        """ return tag weight """
        return self.counter

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')


class Recipe(models.Model):
    """ Model of recipe """
    STATUS_CHOICES = (
        (u'P', _('published')),
        (u'd', _('draft')),
        (u'i', _('idea')),
    )
    COMPLEXITY_CHOICES = (
        (1, _('еasy')),
        (2, _('medium')),
        (3, _('hard')),
    )
    title = models.CharField(max_length=250, unique=True,
                             verbose_name=_('title'))
    url = models.CharField(max_length=250, default='', unique=True, blank=True,
                           verbose_name=_('recipe url'))
    status = models.CharField(max_length=2, default=u'i',
                              choices=STATUS_CHOICES,
                              verbose_name=_('status'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 verbose_name=_('category'))
    complexity = models.IntegerField(default=1, choices=COMPLEXITY_CHOICES,
                                     verbose_name=_('complexity'))
    description = models.TextField(blank=True, verbose_name=_('description'))
    time = models.IntegerField(default=0, null=True, blank=True,
                               verbose_name=_('time'),
                               help_text=_("Total time for cooking, "
                                           "in minutes"))
    manually_weight = models.IntegerField(default=None, null=True, blank=True,
                                          verbose_name=_('weight'),
                                          help_text=_("Weight after cooking, "
                                                      "in grams"))
    manually_energy = models.DecimalField(default=None, null=True, blank=True,
                                          max_digits=7, decimal_places=3,
                                          verbose_name=_('energy'))
    manually_protein = models.DecimalField(default=None, null=True, blank=True,
                                           max_digits=7, decimal_places=3,
                                           verbose_name=_('protein'))
    manually_fat = models.DecimalField(default=None, null=True, blank=True,
                                       max_digits=7, decimal_places=3,
                                       verbose_name=_('fat'))
    manually_carbohydrate = models.DecimalField(default=None, null=True,
                                                blank=True, max_digits=7,
                                                decimal_places=3,
                                                verbose_name=_('carbohydrate'))
    weight = models.IntegerField(default=0, verbose_name=_('weight'),
                                 help_text=_("Weight after cooking, in grams"))
    energy = models.DecimalField(default=0, max_digits=7, decimal_places=3,
                                 verbose_name=_('energy'))
    protein = models.DecimalField(default=0, max_digits=7, decimal_places=3,
                                  verbose_name=_('protein'))
    fat = models.DecimalField(default=0, max_digits=7, decimal_places=3,
                              verbose_name=_('fat'))
    carbohydrate = models.DecimalField(default=0, max_digits=7,
                                       decimal_places=3,
                                       verbose_name=_('carbohydrate'))
    image = AjaxImageField(null=True, blank=True, upload_to='images',
                           max_width=1024, max_height=768, crop=True,
                           verbose_name=_('image'))
    thumbnail = ImageSpecField(source='image',
                               processors=[ResizeToFill(400, 300)],
                               format='JPEG', options={'quality': 90})
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('tags'),
                                  help_text=_('tags'))

    def __str__(self):
        return self.title

    def calculate(self):
        """ calculate recipe energy, protein, fat and carbohydrate """
        energy = 0
        protein = 0
        fat = 0
        carbohydrate = 0
        weight = 0
        for ingredient in self.recipeingredient_set.all():
            iwt = ingredient.weight
            weight = weight + iwt
            if ingredient.ingredient.energy:
                energy += float(ingredient.ingredient.energy) * iwt / 100
            if ingredient.ingredient.protein:
                protein += ingredient.ingredient.protein * iwt / 100
            if ingredient.ingredient.fat:
                fat += ingredient.ingredient.fat * iwt / 100
            if ingredient.ingredient.carbohydrate:
                carbohydrate += ingredient.ingredient.carbohydrate * iwt / 100
        if self.manually_weight:
            weight = self.manually_weight
        if weight:
            self.energy = float(energy / weight * 100) \
                    if self.manually_energy is None else self.manually_energy
            self.protein = float(protein / weight * 100) \
                    if self.manually_protein is None else self.manually_protein
            self.fat = float(fat / weight * 100) \
                    if self.manually_fat is None else self.manually_fat
            self.carbohydrate = float(carbohydrate / weight * 100) \
                    if self.manually_carbohydrate is None \
                    else self.manually_carbohydrate
            self.weight = weight if self.manually_weight is None \
                    else self.manually_weight

    def count_tags(self):
        """ count recipes in tags """
        for tag in self.tags.all():
            counter = Recipe.objects.filter(models.Q(tags__name=tag.name),
                                            status=u'P').count()
            tag = Tag.objects.get(pk=tag.id)
            tag.counter = counter
            tag.save()

    def fullness(self):
        """ return recipe fullnes """
        fullness = 0
        if self.image:
            fullness = fullness + 20
        if self.description:
            fullness = fullness + 10
        ok_gram = True
        ok_energy = True
        ok_nutrients = True
        ingredients = self.recipeingredient_set.all()
        if ingredients:
            fullness = fullness + 20
            for ingredient in ingredients:
                if ingredient.roughly:
                    ok_gram = False
                if ingredient.ingredient.energy is None:
                    ok_energy = False
                if ingredient.ingredient.protein is None or \
                        ingredient.ingredient.fat is None or \
                        ingredient.ingredient.carbohydrate is None:
                    ok_nutrients = False
            if ok_gram:
                fullness = fullness + 20
            if ok_energy:
                fullness = fullness + 20
            if ok_nutrients:
                fullness = fullness + 5
        if self.recipeimage_set.all():
            fullness = fullness + 5
        return '%i%%' % fullness
    fullness.short_description = _('fullness')

    def recipe_tags(self):
        """ return recipe tags, comma separated """
        return ", ".join([t.name for t in self.tags.all()])
    recipe_tags.short_description = _('tags')

    def recipe_ingredients(self, maximum=3, weight=False, more=False):
        """ return list of recipe ingredients """
        ingredients = []
        for i in self.recipeingredient_set.all():
            if weight:
                ingr = "{}: {} {}".format(i.ingredient.name, i.weight, _('gr'))
            else:
                ingr = i.ingredient.name
            ingredients.append(ingr)
        return ', '.join(ingredients[0:maximum]) + \
                    (' ...' if (maximum < len(ingredients) and more) else '')
    recipe_ingredients.short_description = _('ingredients')

    def fix_url(self):
        """ convert recipe title to translit [a-zA-Z] """
        self.url = transliterate(self.title)

    def has_roughly(self):
        """ return True if recipe has roughly ingridient """
        has_roughly = False
        for i in self.recipeingredient_set.all():
            if i.roughly:
                has_roughly = True
        return has_roughly
    has_roughly.short_description = _('Has roughly')

    class Meta:
        verbose_name = _('recipe')
        verbose_name_plural = _('recipes')


class RecipeIngredient(models.Model):
    """ Model of ingredients on recipe """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name=_('recipe'))
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name=_('ingredient'))
    weight = models.IntegerField(default=0, null=True, blank=True,
                                 verbose_name=_('weight in gram'))
    quantity = models.DecimalField(max_digits=4, decimal_places=2, default=0,
                                   verbose_name=_('quantity on additional unit')
                                   )
    unit = models.ForeignKey(Unit, default=None, null=True, blank=True,
                             on_delete=models.CASCADE,
                             verbose_name=_('additional unit'))
    roughly = models.BooleanField(default=False, verbose_name=_('roughly'))

    def __str__(self):
        return self.ingredient.name

    class Meta:
        verbose_name = _('ingredient')
        verbose_name_plural = _('ingredients')


class RecipeImage(models.Model):
    """ Model of recipe image """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name=_('recipe'))
    image = AjaxImageField(null=True, blank=True, upload_to='images',
                           max_width=1024, max_height=768, crop=True,
                           verbose_name=_('image'))
    thumbnail = ImageSpecField(source='image',
                               processors=[ResizeToFill(400, 300)],
                               format='JPEG', options={'quality': 90})
    title = models.CharField(max_length=250, blank=True,
                             verbose_name=_('title'))

    def __str__(self):
        return _('image') + '-' + str(self.id)

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')
