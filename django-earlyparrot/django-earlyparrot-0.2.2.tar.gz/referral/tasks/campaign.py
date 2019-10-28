import requests
import logging

from django.conf import settings

from celery import Task

logger = logging.getLogger('referral')


class CampaignSubscribeTask(Task):
    ignore_result = True
    name = 'CampaignSubscribeTask'

    def run(self, *args, **kwargs):
        campaign_id = kwargs.get('campaign_id')
        email = kwargs.get('email')
        rh = kwargs.get('rh')
        url = settings.REFERRAL_EARLY_PARROT_BASE_API.format(campaign_id)

        data = {
            'firstName': kwargs.get('firstName'),
            'lastName': kwargs.get('lastName'),
            'email': email,
            'rh': rh,
        }

        if kwargs.get('conversionName'):
            data['conversionName'] = kwargs.get('conversionName')

        try:
            requests.post(url, data=data)
            logger.info('CampaignSubscribeTask: {}-{}-{}'.format(campaign_id, email, rh))
        except Exception as exc:
            logger.error('CampaignSubscribeTask.Exception: {}-{}-{}'.format(campaign_id, email, rh))
            logger.error('CampaignSubscribeTask.Exception: {}'.format(exc))
