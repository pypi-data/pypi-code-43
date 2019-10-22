import pkg_resources

from django.conf import settings

from directory_client_core.base import AbstractAPIClient


class APIFormsClient(AbstractAPIClient):

    endpoints = {
        'ping': 'api/healthcheck/ping/',
        'submission': 'api/submission/',
    }
    version = pkg_resources.get_distribution(__package__).version

    def ping(self):
        return self.get(url=self.endpoints['ping'])

    def submit_generic(self, data):
        return self.post(url=self.endpoints['submission'], data=data)


forms_api_client = APIFormsClient(
    base_url=settings.DIRECTORY_FORMS_API_BASE_URL,
    api_key=settings.DIRECTORY_FORMS_API_API_KEY,
    sender_id=settings.DIRECTORY_FORMS_API_SENDER_ID,
    timeout=settings.DIRECTORY_FORMS_API_DEFAULT_TIMEOUT,
)
