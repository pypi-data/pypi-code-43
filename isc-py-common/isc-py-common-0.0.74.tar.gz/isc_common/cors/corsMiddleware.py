from django.utils.deprecation import MiddlewareMixin


class CorsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        setattr(response, "Access-Control-Allow-Origin", "*")
        return response
