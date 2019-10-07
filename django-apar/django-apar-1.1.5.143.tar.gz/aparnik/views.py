# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http.response import JsonResponse


def install(request):

    context = {
        'title': 'نصب'
    }
    template_name = 'aparnik/index.html'
    return render(request, template_name=template_name, context=context)