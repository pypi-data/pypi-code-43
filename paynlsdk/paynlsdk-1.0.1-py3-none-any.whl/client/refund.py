from paynlsdk.api.client import APIClient


class Refund(object):
    @staticmethod
    def info(refund_id: str):
        """
        Return refund info

        :param refund_id: Refund ID (starts wih "RF-")
        :type refund_id: str
        :return: Info Response
        :rtype: paynlsdk.api.refund.info.Response
        """
        from paynlsdk.api.refund.info import Request
        client = APIClient()
        request = Request(refund_id)
        client.perform_request(request)
        return request.response

    @staticmethod
    def transaction(transaction_id: str,
                    amount: int=None,
                    description: str=None,
                    process_date: str=None,
                    products: dict={},
                    vat_percentage: float=None,
                    exchange_url: str=None):
        """
        Refund a transaction

        :param transaction_id: Transaction ID
        :type transaction_id: str
        :param amount: transaction amount to refund
        :type amount: int
        :param description: refund description
        :type description: str
        :param process_date: date at which refund needs to be processed
                TODO: this *should* be a datetime
        :type process_date: str
        :param products: dictionary of products to refund (keys: product ID, value: quantity)
        :type products: dict
        :param vat_percentage: VAT percentage
        :type vat_percentage: float
        :param exchange_url: URL for the exchange call
        :type exchange_url: str
        :return: Transaction refund response
        :rtype: paynlsdk.api.refund.transaction.Response
        """
        from paynlsdk.api.refund.transaction import Request
        client = APIClient()
        request = Request(transaction_id, amount, description, process_date, products, vat_percentage, exchange_url)
        client.perform_request(request)
        return request.response

    @staticmethod
    def info_request():
        """
        Get a refund info request instance

        :return: The request object that can be configured
        :rtype: paynlsdk.api.refund.info.Request
        """
        from paynlsdk.api.refund.info import Request
        return Request()

    @staticmethod
    def transaction_request():
        """
        Get a refund transaction request instance

        :return: The request object that can be configured
        :rtype: paynlsdk.api.refund.info.Request
        """
        from paynlsdk.api.refund.info import Request
        return Request()
