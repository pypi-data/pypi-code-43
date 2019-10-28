import requests
import logging

from django.apps import apps
from django.conf import settings

from celery import Task

logger = logging.getLogger('referral')


class SubscriberGetTokenTask(Task):
    ignore_result = True
    name = 'SubscriberGetTokenTask'

    def run(self, *args, **kwargs):
        Campaign = apps.get_model(
            app_label='referral',
            model_name='Campaign',
        )
        campaign = Campaign.objects.get(campaign_id=kwargs.get('campaign_id'))
        subscriber = campaign.subscriber_set.get(user__pk=kwargs.get('user_pk'))

        url = settings.REFERRAL_EARLY_PARROT_BASE_API.format(campaign.campaign_id)

        data = {
            'firstName': subscriber.user.first_name,
            'lastName': subscriber.user.last_name,
            'email': subscriber.user.email,
        }

        response = requests.post(url, data=data)

        subscriber.token = response.json().get('user').get('confirmationToken')
        subscriber.save()

        logger.info('SubscriberGetTokenTask: {}-{}'.format(
            campaign.campaign_id,
            subscriber.user.email,
        ))
