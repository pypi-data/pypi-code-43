"""
Django Vegetarian Cookbook, Copyright © 2018 Sergey Panasenko.
Contacts: <sergey.panasenko@gmail.com>
License: https://opensource.org/licenses/AGPL-3.0
"""

from django.urls import include, path, re_path
from django.contrib import admin
from . import views

admin.autodiscover()

urlpatterns = [
    re_path(r'^category/(?P<category_name>[\s\w_\-0-9]+)$',
            views.CategoryView.as_view(), name='recipes_category'),
    re_path(r'^category/(?P<category_name>[\s\w_\-0-9]+)/(?P<page>\d+)/$',
            views.CategoryView.as_view(), name='recipes_category_page'),
    re_path(r'^tags/(?P<tags>[\s\w\,_\-0-9]+)$',
            views.TagsView.as_view(), name='recipes_tags'),
    re_path(r'^tags/(?P<tags>[\s\w\,_\-0-9]+)/(?P<page>\d+)/$',
            views.TagsView.as_view(), name='recipes_tags_page'),
    re_path(r'^recipe/(?P<recipe_name>[A-Za-z_\-0-9]+)$',
            views.DetailView.as_view(), name='recipes_recipe'),
    re_path(r'^ingredient/(?P<ingredient_name>[\s\w_\-0-9%\(\)]+)$',
            views.IngredientView.as_view(), name='recipes_ingredient'),
    path('tags-ingredients', views.TagIngredientsView.as_view(),
         name='recipe_tags_ingredients'),
    re_path(r'^tags-ingredients/(?P<page>\d+)/$',
            views.TagIngredientsView.as_view(),
            name='recipe_tags_ingredients_page'),
    path('search/', views.SearchView.as_view(), name='recipes_search'),
    path('robots.txt', views.RobotsView.as_view(), name='robots'),
    path('sitemap.xml', views.SitemapView.as_view(), name='sitemap'),
    path('ajaximage/', include('ajaximage.urls')),
    re_path(r'^(?P<page>\d+)/$', views.IndexView.as_view(),
            name='recipes_index_page'),
    path('', views.IndexView.as_view(), name='recipes_index'),
]
