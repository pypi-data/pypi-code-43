import os
import json
import threading
from time import time
from .event import push_view_data


class MiddlewareMixin:
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, "process_request"):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, "process_response"):
            response = self.process_response(request, response)
        return response


class DjangoEventMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if os.environ.get("DEBUG"):
            print(exception.__class__.__name__)
            print(exception.message)
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        self.view_func = view_func.__name__

    def process_request(self, request):
        request.start_time = time()

    def process_response(self, request, response):
        request_data = request.POST.dict() or request.GET.dict()
        try:
            response_data = json.loads(json.dumps(response.data, ensure_ascii=False))
        except (json.JSONDecodeError, TypeError, ValueError, AttributeError):
            response_data = response.content.decode("utf-8")
        response_time = time() - request.start_time
        headers = [h for h in request.META if isinstance(h, (int, str, float))]
        kwargs = {
            "method": request.method,
            "path": request.path,
            "uri": request.get_raw_uri(),
            "status": response.status_code,
            "name": self.view_func if hasattr(self, 'view_func') else 'NotRouting',
            "headers": headers,
            "request_data": request_data,
            "response_data": response_data,
            "response_time": response_time,
        }
        trd = threading.Thread(target=push_view_data, kwargs=kwargs)
        trd.start()
        # trd.join()
        return response
