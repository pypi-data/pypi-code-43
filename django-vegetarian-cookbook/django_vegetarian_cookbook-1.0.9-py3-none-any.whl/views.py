"""
Django Vegetarian Cookbook, Copyright © 2018 Sergey Panasenko.
Contacts: <sergey.panasenko@gmail.com>
License: https://opensource.org/licenses/AGPL-3.0
"""
from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse
from django.views.generic.base import View, TemplateView
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

from vegetarian_cookbook import appsettings
from vegetarian_cookbook.models import Recipe, Category, Tag, Ingredient
from vegetarian_cookbook.search import Search


class IndexView(TemplateView):
    """ home page """
    template_name = "vegetarian_cookbook/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.kwargs['page'] if 'page' in self.kwargs else 1
        recipes_list = Recipe.objects.all().filter(status=u'P').order_by('-id')
        try:
            paginator = Paginator(recipes_list, appsettings.RECIPES_IN_LIST)
            recipes = paginator.page(page)
        except PageNotAnInteger:
            recipes = paginator.page(1)
        except EmptyPage:
            raise Http404("Not correct page number")
        recipes.base_url = ''
        context['recipes'] = recipes
        context['title'] = _('All recipes')
        context['seo_description'] = appsettings.SEO_DESCRIPTION
        context['seo_keywords'] = appsettings.SEO_KEYWORDS
        return context


class DetailView(TemplateView):
    """ recipe page """
    template_name = "vegetarian_cookbook/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            recipe_name = self.kwargs['recipe_name']
            if self.request.user.has_perm('vegetarian_cookbook.change_recipe'):
                # admin can see drafts and ideas, users only published
                recipe = Recipe.objects.get(url=recipe_name)
            else:
                recipe = Recipe.objects.get(url=recipe_name, status=u'P')
        except Recipe.DoesNotExist:
            raise Http404("Recipe does not exist")
        context['recipe'] = recipe
        context['seo_description'] = recipe.recipe_ingredients(20, False, True)
        context['seo_keywords'] = recipe.recipe_tags() + ', ' \
            + appsettings.SEO_KEYWORDS
        return context


class TagsView(TemplateView):
    """ tags page """
    template_name = "vegetarian_cookbook/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.kwargs['page'] if 'page' in self.kwargs else 1
        tags = self.kwargs['tags']
        tags_list = tags.split(",")
        recipes_list = Recipe.objects.all().filter(
            Q(tags__name__in=tags_list), status=u'P').distinct().order_by('-id')
        try:
            paginator = Paginator(recipes_list, appsettings.RECIPES_IN_LIST)
            recipes = paginator.page(page)
        except PageNotAnInteger:
            recipes = paginator.page(1)
        except EmptyPage:
            recipes = paginator.page(paginator.num_pages)
        recipes.base_url = reverse('recipes_tags', args=[tags])
        context['recipes'] = recipes
        context['title'] = _('Tags: %(tags)s.') % {'tags': tags}
        context['seo_description'] = appsettings.SEO_DESCRIPTION + \
            _('Tags: %(tags)s.') % {'tags': tags}
        context['seo_keywords'] = tags + ', ' + appsettings.SEO_KEYWORDS
        return context


class CategoryView(TemplateView):
    """ category page """
    template_name = "vegetarian_cookbook/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.kwargs['page'] if 'page' in self.kwargs else 1
        category_name = self.kwargs['category_name']
        try:
            category = Category.objects.get(name=category_name)
            recipes_list = Recipe.objects.filter(
                category=category.id, status=u'P').order_by('-id')
            paginator = Paginator(recipes_list, appsettings.RECIPES_IN_LIST)
            recipes = paginator.page(page)
        except PageNotAnInteger:
            recipes = paginator.page(1)
        except EmptyPage:
            recipes = paginator.page(paginator.num_pages)
        except Category.DoesNotExist:
            raise Http404("Category does not exist")
        recipes.base_url = reverse('recipes_category', args=[category_name])
        context['recipes'] = recipes
        context['title'] = _('Category: %(category)s.') % \
            {'category': category.name}
        context['seo_description'] = appsettings.SEO_DESCRIPTION + \
            _('Category: %(category)s.') % {'category': category.name}
        context['seo_keywords'] = category_name + ', ' \
            + appsettings.SEO_KEYWORDS
        return context


class IngredientView(TemplateView):
    """ ingredient page """
    template_name = "vegetarian_cookbook/ingredient.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ingredient_name = self.kwargs['ingredient_name']
        try:
            ingredient = Ingredient.objects.get(name=ingredient_name)
            recipes = Recipe.objects.all().filter(
                Q(recipeingredient__ingredient__id=ingredient.id), status=u'P')
        except Recipe.DoesNotExist:
            raise Http404("Ingredient does not exist")
        context['ingredient'] = ingredient
        context['recipes'] = recipes
        context['seo_description'] = appsettings.SEO_DESCRIPTION + \
            ingredient_name
        context['seo_keywords'] = ingredient_name + ', ' + \
            appsettings.SEO_KEYWORDS
        return context


class TagIngredientsView(TemplateView):
    """ tag ingredients page """
    template_name = "vegetarian_cookbook/tags_ingredients.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.kwargs['page'] if 'page' in self.kwargs else 1
        tags = Tag.objects.all()
        search = self.request.POST.get('search', '')
        ingredients_list = Ingredient.objects.all()
        if search != '':
            ingredients_list = ingredients_list.filter(name__icontains=search)
        try:
            paginator = Paginator(ingredients_list.order_by('name'),
                                  appsettings.INGREDIENTS_IN_LIST)
            ingredients = paginator.page(page)
        except PageNotAnInteger:
            ingredients = paginator.page(1)
        except EmptyPage:
            ingredients = paginator.page(paginator.num_pages)
        ingredients.base_url = reverse('recipe_tags_ingredients')
        context['tags'] = tags
        context['search'] = search
        context['ingredients'] = ingredients
        context['seo_description'] = appsettings.SEO_DESCRIPTION
        context['seo_keywords'] = appsettings.SEO_KEYWORDS
        return context


class SearchView(View):
    """ search page """

    def get(self, request):
        return self.response(request)

    def post(self, request):
        return self.response(request)

    def response(self, request):
        """ return search as json or html """
        search = Search.collect(request)
        results = Search.results(search, True)
        if request.is_ajax():
            return JsonResponse({'results': results, 'search': search})
        return render(request, 'vegetarian_cookbook/search.html', {
            'search': search,
            'results': results,
            'title': _("Search"),
            'seo_description': appsettings.SEO_DESCRIPTION,
            'seo_keywords': appsettings.SEO_KEYWORDS,
        })


class RobotsView(View):
    """ return robots.txt file """

    def get(self, request):
        robots = render_to_string('vegetarian_cookbook/robots.txt', {
            'url': request.build_absolute_uri().replace('/robots.txt', ''),
        })
        return HttpResponse(robots, content_type="text/plain; charset=utf-8")


class SitemapView(View):
    """ return sitemap """

    def get(self, request):
        recipes = Recipe.objects.all().filter(status=u'P').order_by('-id')
        sitemap = render_to_string('vegetarian_cookbook/sitemap.xml', {
            'recipes': recipes,
            'url': request.build_absolute_uri().replace('/sitemap.xml', ''),
        })
        return HttpResponse(sitemap, content_type="text/xml; charset=utf-8")
