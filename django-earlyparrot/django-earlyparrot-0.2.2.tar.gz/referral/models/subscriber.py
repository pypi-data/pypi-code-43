from django.db import models
from django.conf import settings

from ..tasks import SubscriberGetTokenTask


class Subscriber(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    campaign = models.ForeignKey(
        'referral.Campaign',
        on_delete=models.CASCADE,
    )
    token = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'

    def get_campaign_token(self):
        SubscriberGetTokenTask().s(**{
            'campaign_id': self.campaign.campaign_id,
            'user_pk': self.user.pk,
        }).apply_async()
