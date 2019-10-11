from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from . import models


@csrf_exempt
def webhook(request, uid):
    if request.method != 'POST':
        return HttpResponseBadRequest("Method not allowed.")
    webhook = get_object_or_404(models.Webhook, uid=uid)
    input = models.Input()
    input.settings =  webhook.settings
    input.internal_source = False
    input.format = 'form' if request.META['CONTENT_TYPE'] == 'application/x-www-form-urlencoded' else 'json'
    input.raw_content = request.body.decode('utf-8')
    input.save()
    input.notify()
    return HttpResponse("Ok")
