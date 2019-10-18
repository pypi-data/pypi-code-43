# Django Vegetarian Cookbook, Copyright © 2018 Sergey Panasenko. Contacts: <sergey.panasenko@gmail.com>
# License: https://opensource.org/licenses/AGPL-3.0

from django.test import TestCase
from .models import Category, Recipe, Ingredient, RecipeIngredient

class RecipeMethodTests(TestCase):

    def test_calculate(self):
        """
        test calculate energy and nutrients
        """
        recipe = Recipe()
        recipe.calculate()
        self.assertEqual(recipe.energy, None)

        recipe = Recipe(weight=100)
        recipe.calculate()
        self.assertEqual(recipe.energy, 0)

        category = Category(name='Cat1')
        category.save()
        recipe = Recipe(category=category)
        recipe.save()
        ingredient = Ingredient(name='test1', energy=100, protein=1, fat=2, carbohydrate=3)
        ingredient.save()
        recipeingredient = RecipeIngredient(recipe=recipe, ingredient=ingredient, weight=100)
        recipeingredient.save()
        recipe.calculate()
        self.assertEqual(recipe.energy, 100)
        self.assertEqual(recipe.protein, 1)
        self.assertEqual(recipe.fat, 2)
        self.assertEqual(recipe.carbohydrate, 3)

        ingredient = Ingredient(name='test2', energy=300, protein=5, fat=10, carbohydrate=15)
        ingredient.save()
        recipeingredient = RecipeIngredient(recipe=recipe, ingredient=ingredient, weight=300)
        recipeingredient.save()
        recipe.calculate()
        self.assertEqual(recipe.energy, 250)
        self.assertEqual(recipe.protein, 4)
        self.assertEqual(recipe.fat, 8)
        self.assertEqual(recipe.carbohydrate, 12)

