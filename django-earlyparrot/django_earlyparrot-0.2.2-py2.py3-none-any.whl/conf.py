import logging

from appconf import AppConf

from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class ReferralConfig(AppConf):
    APP_NAME = 'referral'

    EARLY_PARROT_BASE_API = 'https://admin.earlyparrot.com/api/campaigns/{}/subscribe'

    CAMPAIGN_STATUS_ACTIVE = 'A'
    CAMPAIGN_STATUS_INACTIVE = 'I'
    CAMPAIGN_STATUS_DEFAULT = CAMPAIGN_STATUS_ACTIVE

    CAMPAIGN_STATUS_CHOICES = (
        (CAMPAIGN_STATUS_ACTIVE, 'Active'),
        (CAMPAIGN_STATUS_INACTIVE, 'Inactive'),
    )

    # Webhooks type names
    NEW_REWARD_AWARED = 'NewReward'

    CONVERSION_NAME = 'SIGNUP_COMPLETED'
