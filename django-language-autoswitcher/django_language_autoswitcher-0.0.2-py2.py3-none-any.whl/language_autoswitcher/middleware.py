from django.conf import settings
from django.utils import translation
from django.utils.cache import patch_vary_headers


class LanguageAutoSwitcherMiddleware:
    languages_key = ["lng"]
    language_cookie_name = "lng"

    def __init__(self, get_response):
        self.get_response = get_response
        if hasattr(settings, "LANGUAGES_KEY"):
            self.languages_key = settings.LANGUAGES_KEY
        if hasattr(settings, "LANGUAGE_COOKIE_NAME"):
            self.language_cookie_name = settings.LANGUAGE_COOKIE_NAME

    def process_request(self, request):
        language = None
        for kw in self.languages_key:
            language = request.GET.get(kw)
            if language:
                break
        if not language:
            for kw in self.languages_key:
                language = request.COOKIES.get(kw)
                if language:
                    break
        if not language:
            if 'HTTP_ACCEPT_LANGUAGE' in request.META:
                language = request.META['HTTP_ACCEPT_LANGUAGE'][:2]
        if not language:
            language = "en"
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
        return request

    def process_response(self, response):
        if self.language_cookie_name not in response.cookies:
            response.set_cookie(self.language_cookie_name,
                                translation.get_language())
        patch_vary_headers(response, ('Accept-Language', ))
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response

    def __call__(self, request):
        request = self.process_request(request)
        response = self.get_response(request)
        response = self.process_response(response)
        return response
