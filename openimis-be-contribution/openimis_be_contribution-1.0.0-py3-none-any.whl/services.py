
from .models import Premium
from django.db.models import Sum


class ByPolicyPremiumsAmountService(object):

    def __init__(self, user):
        self.user = user

    def request(self, policy_id):
        return Premium.objects.filter(
            policy_id=policy_id
        ).exclude(
            is_photo_fee=True
        ).aggregate(Sum('amount'))['amount__sum']
