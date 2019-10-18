from django.views.generic import TemplateView
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
)

from .exceptions import InvalidPathException, PageNotFoundException
from .utils import get_page_by_path

import logging

logger = logging.getLogger(__name__)


class PageView(TemplateView):
    def render_to_response(self, context, **response_kwargs):
        try:
            rendered_page = get_page_by_path(self, self.request, logger)

        except InvalidPathException:
            return HttpResponseBadRequest()

        except PageNotFoundException:
            return HttpResponseNotFound(
                'Page ({}) not found'.format(self.request.get_full_path()))

        else:
            return HttpResponse(rendered_page)
