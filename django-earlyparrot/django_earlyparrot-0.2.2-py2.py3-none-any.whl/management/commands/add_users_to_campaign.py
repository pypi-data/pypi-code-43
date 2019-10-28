import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from ...helpers import normalize_email
from ...models import Campaign

logger = logging.getLogger('referral')


class Command(BaseCommand):
    help = ('Add users to a campaign')
    missing_args_message = 'You must provide a campaign ID and CSV file path.'

    def add_arguments(self, parser):
        parser.add_argument('-c', '--campaign', nargs='+', type=str)
        parser.add_argument('-f', '--file', nargs='+', type=str)

    def _read_emails_from_path(self, filepath):
        emails = []

        with open(filepath) as file:
            emails = file.readlines()

        return emails

    def handle(self, *args, **options):
        campaign_id = options.get('campaign')[0]
        filepath = options.get('file')[0]

        logger.info('Command.add_users_to_campaign: {}'.format(campaign_id))

        try:
            campaign = Campaign.objects.get(campaign_id=campaign_id)
            emails = self._read_emails_from_path(filepath)

            for email in emails:
                email = normalize_email(email)

                try:
                    user = get_user_model().objects.get(email=email)
                    campaign.add_subscriber(user)
                    logger.info('User {} added to campaign {}'.format(email, campaign_id))
                except ObjectDoesNotExist:
                    logger.error('User {} DoesNotExist'.format(email))

        except ObjectDoesNotExist:
            logger.error('Campaign {} DoesNotExist'.format(campaign_id))
