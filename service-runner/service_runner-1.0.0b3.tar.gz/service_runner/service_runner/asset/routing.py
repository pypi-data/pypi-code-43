from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/webssh/(?P<host_id>\d+)/$', consumers.WebsshConsumer),
    # url(r'^ws/webssh/$', consumers.WebsshConsumer),
]
