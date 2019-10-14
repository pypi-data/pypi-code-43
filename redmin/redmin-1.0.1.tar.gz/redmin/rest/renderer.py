from rest_framework.renderers import BrowsableAPIRenderer as RestBrowsableAPIRenderer
from rest_framework.renderers import JSONRenderer as RestJSONRenderer

from redmin.utils import attr
from django.conf import settings


class BrowsableAPIRenderer(RestBrowsableAPIRenderer):
    template = 'redmin/rest/api.html'

    def get_context(self, data, accepted_media_type, renderer_context):
        context = super().get_context(data, accepted_media_type, renderer_context)
        context["redmin_page_title"] = attr(settings, "REST_HTML_TITLE", "Rest ")
        return context


class JSONRenderer(RestJSONRenderer):
    charset = 'utf-8'
    pass
