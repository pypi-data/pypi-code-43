from django.conf.urls import url

from .views import (
    GetQuizView,
    ValidateUserTypeformView,
    InvalidateUserTypeformView,
)

app_name = 'typeform_feedback'

urlpatterns = [
    url(r'^generic/(?P<quiz_slug>[a-z A-Z _]+)/$', GetQuizView.as_view(), name='get-quiz'),
    url(r'^responses/validate/(?P<uuid>[0-9a-f-]+)', ValidateUserTypeformView.as_view(), name='validate'),
    url(r'^responses/invalidate/(?P<uuid>[0-9a-f-]+)', InvalidateUserTypeformView.as_view(), name='invalidate'),
]
