"""djangoldp project URL Configuration"""
from django.conf.urls import url
from .views import PendingResourcesViewSet
from .views import ValidatedResourcesByStepViewSet

urlpatterns = [
    url(r'^steps/(?P<id>.+)/resources/validated/', ValidatedResourcesByStepViewSet.urls(model_prefix="resources-validated")),
    url(r'^resources/pending/', PendingResourcesViewSet.urls(model_prefix="resources-pending")),
]