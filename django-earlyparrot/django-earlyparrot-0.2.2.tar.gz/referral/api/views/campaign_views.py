from django.conf import settings

from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Campaign
from ..serializers import CampaignSerializer, CampaignSubscribeSerializer


class CampaignViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated, )
    lookup_field = 'campaign_id'
    lookup_url_kwarg = 'campaign_id'

    serializers = {
        'default': CampaignSerializer,
        'list': CampaignSerializer,
        'subscribe': CampaignSubscribeSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    def get_queryset(self):
        queryset = Campaign.objects.filter(status=settings.REFERRAL_CAMPAIGN_STATUS_ACTIVE)

        if self.action == 'list':
            queryset = queryset.filter(users__email=self.request.user.email)

        return queryset

    @action(methods=['post'], detail=True, url_path='subscribe')
    def subscribe(self, request, campaign_id):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_from=request.user)
        return Response(serializer.data, status.HTTP_200_OK)
