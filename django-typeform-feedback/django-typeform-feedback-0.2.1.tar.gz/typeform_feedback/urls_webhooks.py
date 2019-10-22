from django.conf.urls import url

from .views import GenericTypeformWebhookView

app_name = 'typeform_feedback'


urlpatterns = [
    url(r'^generic/$', GenericTypeformWebhookView.as_view(), name='generic-typeform'),
]
