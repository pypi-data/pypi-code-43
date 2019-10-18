from django.conf.urls import url
from django.conf import settings

from .views import PageView


app_name = 'deeppages'


def get_deeppages_path():
    try:
        path = settings.DEEP_PAGES_URL_NAME
    except AttributeError:
        path = '__deep_page_view__'

    return path


urlpatterns = [
    url('', PageView.as_view(), name=get_deeppages_path()),
]
