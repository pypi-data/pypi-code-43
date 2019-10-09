from typing import List, Dict

from paynlsdk.api.client import APIClient
from paynlsdk.objects import ServicePaymentProfile


class PaymentMethods(object):
    @staticmethod
    def get_list(payment_method_id: int=None) -> Dict[int, ServicePaymentProfile]:
        """
        Gets the list of payment methods.

        :param payment_method_id: payment method ID (defaults to 10, or iDeal)
        :type payment_method_id: int
        :return: List of banks
        :rtype: List[ServicePaymentProfile]
        """
        from paynlsdk.api.transaction.getservicepaymentoptions import Request
        client = APIClient()
        request = Request()
        client.perform_request(request)
        profiles = request.response.payment_profiles
        if payment_method_id is None:
            return profiles
        elif payment_method_id in profiles:
            return {payment_method_id: profiles[payment_method_id]}
        raise KeyError('Payment methos ID "{}" is not found in the result dictionary'.format(payment_method_id))


