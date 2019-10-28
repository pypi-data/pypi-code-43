import logging

from django.contrib.auth import get_user_model
from django.http import HttpResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from ...models import Campaign
from ...signals_define import referral_reward_acquired

logger = logging.getLogger('referral')


class RewardAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        status_code = status.HTTP_404_NOT_FOUND
        webhook_data = request.data

        campaign_id = webhook_data.get('campaignId')
        email = webhook_data.get('email')

        try:
            campaign = Campaign.objects.get(campaign_id=campaign_id)
            user_from = campaign.users.get(email=email)

            referral_reward_acquired.send(
                sender=campaign.__class__,
                user_from=user_from,
                reward_data=webhook_data,
            )
            status_code = status.HTTP_200_OK
            logger.info('RewardAPIView OK: {}-{}'.format(campaign_id, email))

        except Campaign.DoesNotExist:
            logger.error('Campaign.DoesNotExist: {}-{}'.format(campaign_id, email))

        except get_user_model().DoesNotExist:
            logger.error('User.DoesNotExist: {}-{}'.format(campaign_id, email))
        except Exception as exc:
            logger.error('RewardAPIView.Exception: {}'.format(exc))

        return HttpResponse(status=status_code)
