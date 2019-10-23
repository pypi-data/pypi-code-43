# Imports from Django.
from django.urls import include
from django.urls import path


# Imports from other dependencies.
from rest_framework import routers


# Imports from government.
from government.viewsets import BodyViewSet
from government.viewsets import JurisdictionViewSet
from government.viewsets import OfficeViewSet
from government.viewsets import PartyViewSet


router = routers.DefaultRouter()

router.register(r"bodies", BodyViewSet)
router.register(r"jurisdictions", JurisdictionViewSet)
router.register(r"offices", OfficeViewSet)
router.register(r"parties", PartyViewSet)

urlpatterns = [path("api/", include(router.urls))]
