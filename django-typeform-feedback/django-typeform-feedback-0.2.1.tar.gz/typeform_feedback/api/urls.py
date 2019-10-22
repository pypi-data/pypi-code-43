from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from .views import UserTypeformViewSet

app_name = 'typeform_feedback'

router = DefaultRouter()
router.register(r'', UserTypeformViewSet, base_name='action')

urlpatterns = [
    url(r'^action/', include(router.urls)),
]
