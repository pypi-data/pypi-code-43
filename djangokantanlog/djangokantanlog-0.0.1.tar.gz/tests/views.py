from django.views.generic.base import View
from django.http import HttpResponse
from .models import TObject
from logging import getLogger


logger = getLogger(__name__)


class ProfileView(View):

    http_method_names = [
        'get',
    ]

    def get(self, request, *args, **kwargs):
        u = str(request.user)
        return HttpResponse(
            ('{"username": "%s"}' % u),
            content_type='application/json',
        )


class CreateView(View):

    http_method_names = [
        'post',
    ]

    def post(self, request, *args, **kwargs):
        tobject = TObject(name='init', level=1)
        res = tobject.save()
        return HttpResponse(
            '{"res": "%s"}' % str(res),
            content_type='application/json'
        )


class UpdateView(View):

    http_method_names = [
        'post',
    ]

    def post(self, request, *args, **kwargs):
        tobject = TObject.objects.get(name='original')
        tobject.level = 777
        tobject.save()
        return HttpResponse(
            '{"res": "OK"}',
            content_type='application/json'
        )
