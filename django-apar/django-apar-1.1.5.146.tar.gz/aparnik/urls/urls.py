from django.conf.urls import url, include
from aparnik.views import install

app_name='aparnik'

urlpatterns = [
    url(r'^install$', install, name='install'),
    url(r'^shops/', include('aparnik.packages.shops.urls.urls', namespace='shops')),
]
