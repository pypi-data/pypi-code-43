# Imports from Django.
from django.urls import include
from django.urls import path


# Imports from other dependencies.
from rest_framework.routers import DefaultRouter


# Imports from entity.
from entity.viewsets import ImageTagViewSet
from entity.viewsets import OrganizationClassificationViewSet
from entity.viewsets import OrganizationViewSet
from entity.viewsets import PersonViewSet


router = DefaultRouter()
router.register(r"people", PersonViewSet)
router.register(r"organizations", OrganizationViewSet)
router.register(r"image-tags", ImageTagViewSet)
router.register(
    r"organization-classifications", OrganizationClassificationViewSet
)

urlpatterns = [path("api/", include(router.urls))]
