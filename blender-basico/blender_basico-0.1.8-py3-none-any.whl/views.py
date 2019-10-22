from django.shortcuts import render
from django.contrib import messages


def index(request):
    return render(request, 'blender_basico/base.pug', {})


def index_with_alert(request):
    messages.add_message(request, messages.INFO, 'This is an info message.')
    messages.add_message(request, messages.SUCCESS, 'This is a success message.')
    return render(request, 'blender_basico/base.pug')
