import datetime
import json
import logging
import traceback

from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from redmin.utils import attr, get_url_prefix

logger = logging.getLogger(__name__)

debug = attr(settings, 'DEBUG')


class LogMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response

    def process_request(self, request):
        self.time = datetime.datetime.now()
        data = ""
        if request.method in ["POST", "PUT"]:
            post_data = request.POST
            if post_data:
                data = " form:%s" % json.dumps(request.POST)
            else:
                body = attr(request, "body")
                if body:
                    data = f" body:{body}"
        self.data = data
        pass

    def process_response(self, request, response):
        duration = (datetime.datetime.now() - self.time).microseconds
        prefix = get_url_prefix(request)
        content = ""
        content_type = response['Content-Type']
        if content_type.split(";")[0].lower() in ['application/json', "text/xml"] and response.content:
            content = "response:%s" % response.content.decode('raw_unicode_escape')

        name = attr(request, "user.username")
        user_info = f"user:{name}" if name else ""
        path = request.get_full_path()
        ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR') or "no-ip"
        message = f'{ip} {request.method} "{prefix}{path}"{self.data} {response.status_code} {duration}ms {len(response.content)}b "{content_type}" {content} {user_info}'
        try:
            logger.info(message)
        except:
            pass
        return response

    def process_exception(self, request, exception):
        meta = request.META
        ip = meta.get('HTTP_X_FORWARDED_FOR') or meta.get('REMOTE_ADDR') or "no-ip"
        path = request.get_full_path()
        trace = traceback.format_exc()
        logger.error(f'{ip} {request.method} {path},process_exception: {json.dumps({"trace": trace})}')
        if debug:
            try:
                logger.error(trace)
            except Exception:
                pass

        if request.GET.get("debug") == '100':
            return HttpResponse(trace, content_type="application/json")
