"""
Django Vegetarian Cookbook, Copyright © 2018 Sergey Panasenko.
Contacts: <sergey.panasenko@gmail.com>
License: https://opensource.org/licenses/AGPL-3.0
"""
import math
from django.db.models import Q, Min, Max
from django.urls import reverse

from vegetarian_cookbook.models import Recipe, Category
from vegetarian_cookbook import appsettings


class Search:
    """ Search in recipes """
    @staticmethod
    def collect(request):
        """ collect search data and range """
        search = {
            'categories': [],
            'complexity_choices': [],
            'query': request.POST.get(
                'query', request.GET.get('query', '')).lower().strip(),
            'in_name': request.POST.get('in_name', False),
            'in_ingredient': request.POST.get('in_ingredient', False),
            'in_tag': request.POST.get('in_tag', False),
        }
        for cat in Category.objects.all():
            search['categories'].append({
                "id": cat.id,
                "name": cat.name,
                "checked": request.POST.get('category-%i' % cat.id, False)
            })
        for key, value in Recipe.COMPLEXITY_CHOICES:
            search['complexity_choices'].append({
                'id': key,
                'name': value,
                'checked': request.POST.get('complexity-%i' % key, False)
            })
        recipes = Recipe.objects.filter(status=u'P')
        if search['query'] != '':
            recipes = Search._search_in_name_ingredient_tag(recipes, search)
        for value in ['energy', 'time', 'protein', 'fat', 'carbohydrate']:
            minmax = recipes.aggregate(Min(value), Max(value))
            if not minmax[value + '__min']:
                recipes = Recipe.objects.filter(status=u'P')
                minmax = recipes.aggregate(Min(value), Max(value))
            search[value] = {}
            search[value]['min'] = math.floor(minmax[value + '__min'])
            search[value]['max'] = math.floor(minmax[value + '__max'])
            search[value]['cmin'] = int(
                request.POST.get(value + '_min', search[value]['min']))
            search[value]['cmax'] = int(
                request.POST.get(value + '_max', search[value]['max']))
            if search[value]['cmin'] < search[value]['min']:
                search[value]['cmin'] = search[value]['min']
            if search[value]['cmax'] > search[value]['max']:
                search[value]['cmax'] = search[value]['max']
        return search

    @staticmethod
    def results(search, as_dict=None):
        """ return list of recipes by search query """
        if search is None:
            search = {}
        res = Recipe.objects.filter(status=u'P').all()
        if search['query'] != '':
            res = Search._search_in_name_ingredient_tag(res, search)
        # search in some categories
        query = False
        for category in search['categories']:
            if category['checked']:
                query_cat = Q(category=category['id'])
                query = query_cat if not query else query | query_cat
        if query:
            res = res.filter(query)

        # by complexity
        query = False
        for complexity in search['complexity_choices']:
            if complexity['checked']:
                query_comp = Q(complexity=complexity['id'])
                query = query_comp if not query else query | query_comp
        if query:
            res = res.filter(query)

        for param in ['energy', 'time', 'protein', 'fat', 'carbohydrate']:
            if search[param]['cmin'] != search[param]['min']:
                kwargs = {'{}__gte'.format(param): search[param]['cmin'], }
                res = res.filter(**kwargs)
            if search[param]['cmax'] != search[param]['max']:
                kwargs = {'{}__lte'.format(param): search[param]['cmax'], }
                res = res.filter(**kwargs)

        max_recs = appsettings.RECIPES_IN_SEARCH
        results = res.filter(status=u'P').distinct().order_by('-id')[0:max_recs]

        if not as_dict:
            return results

        data = []
        for result in results:
            i = {
                'pk': result.pk,
                'title': result.title,
                'url': reverse('recipes_recipe', args=[result.url]),
                'energy': int(round(result.energy)),
                'thumbail': result.thumbnail.url,
                'category': result.category.name,
                'category_img': result.category.thumbnail.url,
            }
            data.append(i)
        return data

    @staticmethod
    def _search_in_name_ingredient_tag(recipes, search):
        # by recipe name
        qnname = Q(title__icontains=search['query'])
        # by ingridient name
        qingr = Q(recipeingredient__ingredient__name__icontains=search[
            'query'])
        # by tag name
        qtag = Q(tags__name__icontains=search['query'])
        query = False
        all_empty = not search['in_name'] and \
                    not search['in_ingredient'] and \
                    not search['in_tag']
        if search['in_name'] or all_empty:
            query = qnname
        if search['in_ingredient'] or all_empty:
            query = qingr if not query else query | qingr
        if search['in_tag'] or all_empty:
            query = qtag if not query else query | qtag
        if query:
            recipes = recipes.filter(query).distinct()
        return recipes
