from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from .views import CampaignViewSet, RewardAPIView

app_name = 'referral'

router = DefaultRouter()

router.register(r'campaigns', CampaignViewSet, base_name='campaign')

urlpatterns = [
    url(r'^webhooks/2XliDq2pdp1szRJ0LR9s2598G/$', RewardAPIView.as_view(), name='reward-awared'),
    url(r'^', include(router.urls)),
]
