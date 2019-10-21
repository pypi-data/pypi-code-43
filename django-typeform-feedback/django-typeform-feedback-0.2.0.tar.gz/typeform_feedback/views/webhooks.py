import logging
import json

from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from ..tasks import UpdateGenericTypeformTask
from ..decorators import ensure_request

decorators = [csrf_exempt, ensure_request]
logger = logging.getLogger('typeform')


@method_decorator(decorators, name='dispatch')
class GenericTypeformWebhookView(View):

    def post(self, request):
        logger.info('Feedback typeform request received')
        data = json.loads(request.body.decode('utf-8'))
        UpdateGenericTypeformTask().delay(
            response_from_typeform=data,
        )
        return HttpResponse('')
