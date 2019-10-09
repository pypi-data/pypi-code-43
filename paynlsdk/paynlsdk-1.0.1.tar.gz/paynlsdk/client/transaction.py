from datetime import datetime

from paynlsdk.api.client import APIClient
from paynlsdk.objects import TransactionData, TransactionStartStatsData, SalesData, TransactionEndUser, BankDetails

from typing import List


class Transaction(object):
    @staticmethod
    def approve(order_id: str, entrance_code: str=None):
        """
        Approve a transaction

        :param order_id: order ID
        :type order_id: str
        :param entrance_code: entrance code
        :type entrance_code: str
        :return: Result of the approval
        :rtype:  bool
        """
        response = Transaction.approve_response(order_id, entrance_code)
        return response.result

    @staticmethod
    def decline(order_id: str, entrance_code: str=None):
        """
        Decline a transaction

        :param order_id: order ID
        :type order_id: str
        :param entrance_code: entrance code
        :type entrance_code: str
        :return: Result of the decline
        :rtype:  bool
        """
        response = Transaction.decline_response(order_id, entrance_code)
        return response.result

    @staticmethod
    def capture(transaction_id: str, products: dict={}, tracktrace: str=None):
        """
        Capture a transaction

        :param transaction_id: order ID
        :type transaction_id: str
        :param products: entrance code
        :type products: dict (keys: product id, value: quantity)
        :param tracktrace: track and trace code
                Some payment methods require proof of shipment. Provide the Track&Trace code if available/applicable
        :type tracktrace: str
        :return: Result of the capture
        :rtype:  bool
        """
        response = Transaction.capture_response(transaction_id, products, tracktrace)
        return response.result

    @staticmethod
    def void(transaction_id: str):
        """
        Decline a transaction

        :param transaction_id: transaction ID
        :type transaction_id: str
        :return: Result of the decline
        :rtype:  bool
        """
        response = Transaction.void_response(transaction_id)
        return response.result

    @staticmethod
    def get_banks() -> List[BankDetails]:
        """
        Gets the list of banks.

        :return: List of banks
        :rtype: List[BankDetails]
        """
        from paynlsdk.api.transaction.getbanks import Request
        client = APIClient()
        request = Request()
        client.perform_request(request)
        return request.response.banks

    @staticmethod
    def get_service(payment_method_id: int):
        """
        Get a transaction getservice :class:`paynlsdk.api.transaction.getservice.Response` instance

        Please note this is a mapping to the :meth:`Transaction.get_service_response` method and is here for consistency

        :return: Transaction getservice response instance
        :rtype: paynlsdk.api.transaction.getservice.Response
        """
        return Transaction.get_service_response(payment_method_id)

    @staticmethod
    def get_service_payment_options(payment_method_id: int=None):
        """
        Get a transaction getservicepaymentoptions :class:`paynlsdk.api.transaction.getservicepaymentoptions.Response` instance

        Please note this is a mapping to the :meth:`Transaction.get_service_payment_options_response` method and is here for consistency

        :param payment_method_id: payment method ID
        :type payment_method_id: int
        :return: Transaction getservicepaymentoptions response instance
        :rtype: paynlsdk.api.transaction.getservicepaymentoptions.Response
        """
        return Transaction.get_service_payment_options_response(payment_method_id)

    @staticmethod
    def info(transaction_id: str, entrance_code: str=None):
        """
        Get a transaction info :class:`paynlsdk.api.transaction.info.Response` instance

        Please note this is a mapping to the :meth:`Transaction.info_response` method and is here for consistency

        :param transaction_id: transaction ID
        :type transaction_id: str
        :param entrance_code: entrance code
        :type entrance_code: str
        :return: Transaction info response instance
        :rtype: paynlsdk.api.transaction.info.Response
        """
        return Transaction.info_response(transaction_id, entrance_code)

    @staticmethod
    def status(transaction_id: str):
        """
        Get transaction status

        Please note this is a mapping to the :meth:`Transaction.status_response` method and is here for consistency

        :param transaction_id: transaction ID
        :type transaction_id: str
        :return: transaction status
        :rtype: paynlsdk.api.transaction.status.Response
        """
        return Transaction.status_response(transaction_id)

    @staticmethod
    def refund(transaction_id: str, amount: int=None, description: str=None, process_date: datetime=None):
        """
        Refund (part of) a transaction

        :param transaction_id: transaction ID
        :type transaction_id: str
        :param amount: transaction amount to refund
        :type amount: int
        :param description: refund description
        :type description: str
        :param process_date: date at which refund needs to be processed
                TODO: this *should* be a datetime
        :type process_date: str
        :return: refund result
        :rtype: paynlsdk.api.transaction.refund.Response
        """
        return Transaction.refund_response(transaction_id, amount, description, process_date)

    @staticmethod
    def start(amount: str,
              ip_address: str,
              finish_url: str,
              payment_option_id: int=None,
              payment_option_sub_id: int=None,
              transaction: TransactionData=None,
              stats_data: TransactionStartStatsData=None,
              end_user: TransactionEndUser=None,
              sale_data: SalesData=None,
              test_mode: bool=False,
              transfer_type: str=None,
              transfer_value: str=None
              ):
        """
        Get a transaction start :class:`paynlsdk.api.transaction.start.Response` instance

        Please note this is a mapping to the :meth:`Transaction.start_response` method and is here for consistency

        :param amount: total order amount(cents)
        :type amount: int
        :param ip_address: IP address
        :type ip_address: str
        :param finish_url: URL to call when finished
        :type finish_url: str
        :param payment_option_id: The ID of the payment option (for iDEAL use 10).
        :type payment_option_id: int
        :param payment_option_sub_id: In case of an iDEAL payment this is the ID of the bank
                See the paymentOptionSubList in the getService function.
        :type payment_option_sub_id: int
        :param transaction:
        :type transaction: TransactionData
        :param stats_data:
        :type stats_data: TransactionStartStatsData
        :param end_user:
        :type end_user: TransactionEndUser
        :param sale_data:
        :type sale_data: SalesData
        :param test_mode: whether or not to perform this transaction start in TEST mode
        :type test_mode: bool
        :param transfer_type: Use transaction, merchant or alliance to change the benificiary owner of the transaction
        :type transfer_type: str
        :param transfer_value: Merchant ID (M-xxxx-xxxx) or order ID
        :type transfer_value: str
        :return: Transaction start response instance
        :rtype: paynlsdk.api.transaction.start.Response
        """
        return Transaction.start_response(amount, ip_address, finish_url, payment_option_id, payment_option_sub_id,
                          transaction, stats_data, end_user, sale_data, test_mode, transfer_type, transfer_value)

    @staticmethod
    def approve_request():
        """
        Get a transaction approve :class:`paynlsdk.api.transaction.approve.Request` instance

        :return: Transaction approve request instance
        :rtype: paynlsdk.api.transaction.approve.Request
        """
        from paynlsdk.api.transaction.approve import Request
        return Request()

    @staticmethod
    def decline_request():
        """
        Get a transaction decline :class:`paynlsdk.api.transaction.decline.Request` instance

        :return: Transaction decline request instance
        :rtype: paynlsdk.api.transaction.decline.Request
        """
        from paynlsdk.api.transaction.decline import Request
        return Request()

    @staticmethod
    def capture_request():
        """
        Get a transaction capture :class:`paynlsdk.api.transaction.capture.Request` instance

        :return: Transaction capture request instance
        :rtype: paynlsdk.api.transaction.capture.Request
        """
        from paynlsdk.api.transaction.capture import Request
        return Request()

    @staticmethod
    def void_request():
        """
        Get a transaction void :class:`paynlsdk.api.transaction.voidauthorization.Request` instance

        :return: Transaction void request instance
        :rtype: paynlsdk.api.transaction.voidauthorization.Request
        """
        from paynlsdk.api.transaction.voidauthorization import Request
        return Request()

    @staticmethod
    def get_banks_request():
        """
        Get a transaction getbanks :class:`paynlsdk.api.transaction.getbanks.Request` instance

        :return: Transaction getbanks request instance
        :rtype: paynlsdk.api.transaction.getbanks.Request
        """
        from paynlsdk.api.transaction.getbanks import Request
        return Request()

    @staticmethod
    def get_service_request():
        """
        Get a transaction getservice :class:`paynlsdk.api.transaction.getservice.Request` instance

        :return: Transaction getservice request instance
        :rtype: paynlsdk.api.transaction.getservice.Request
        """
        from paynlsdk.api.transaction.getservice import Request
        return Request()

    @staticmethod
    def info_request():
        """
        Get a transaction info :class:`paynlsdk.api.transaction.info.Request` instance

        :return: Transaction info request instance
        :rtype: paynlsdk.api.transaction.info.Request
        """
        from paynlsdk.api.transaction.info import Request
        return Request()

    @staticmethod
    def status_request():
        """
        Get a transaction status :class:`paynlsdk.api.transaction.status.Request` instance

        :return: Transaction status request instance
        :rtype: paynlsdk.api.transaction.status.Request
        """
        from paynlsdk.api.transaction.status import Request
        return Request()

    @staticmethod
    def refund_request():
        """
        Get a transaction refund :class:`paynlsdk.api.transaction.refund.Request` instance

        :return: Transaction refund request instance
        :rtype: paynlsdk.api.transaction.refund.Request
        """
        from paynlsdk.api.transaction.refund import Request
        return Request()

    @staticmethod
    def start_request():
        """
        Get a transaction start :class:`paynlsdk.api.transaction.start.Request` instance

        :return: Transaction start request instance
        :rtype: paynlsdk.api.transaction.start.Request
        """
        from paynlsdk.api.transaction.start import Request
        return Request()

    @staticmethod
    def approve_response(order_id: str, entrance_code: str=None):
        """
        Get a transaction approve :class:`paynlsdk.api.transaction.approve.Response` instance

        Please note this will immediately call the API, returning the response instance

        :param order_id: order ID
        :type order_id: str
        :param entrance_code: entrance code
        :type entrance_code: str
        :return: Transaction approve response instance
        :rtype: paynlsdk.api.transaction.approve.Response
        """
        from paynlsdk.api.transaction.approve import Request
        client = APIClient()
        request = Request(order_id, entrance_code)
        client.perform_request(request)
        return request.response

    @staticmethod
    def decline_response(order_id: str, entrance_code: str=None):
        """
        Get a transaction decline :class:`paynlsdk.api.transaction.decline.Response` instance

        Please note this will immediately call the API, returning the response instance

        :param order_id: order ID
        :type order_id: str
        :param entrance_code: entrance code
        :type entrance_code: str
        :return: Transaction decline response instance
        :rtype: paynlsdk.api.transaction.decline.Response
        """
        from paynlsdk.api.transaction.decline import Request
        client = APIClient()
        request = Request(order_id, entrance_code)
        client.perform_request(request)
        return request.response

    @staticmethod
    def capture_response(transaction_id: str, products: dict={}, tracktrace: str=None):
        """
        Get a transaction void :class:`paynlsdk.api.transaction.capture.Response` instance

        Please note this will immediately call the API, returning the response instance

        :param transaction_id: order ID
        :type transaction_id: str
        :param products: entrance code
        :type products: dict (keys: product id, value: quantity)
        :param tracktrace: track and trace code
                Some payment methods require proof of shipment. Provide the Track&Trace code if available/applicable
        :type tracktrace: str
        :return: Transaction capture response instance
        :rtype: paynlsdk.api.transaction.capture.Response
        """
        from paynlsdk.api.transaction.capture import Request
        client = APIClient()
        request = Request(transaction_id, products, tracktrace)
        client.perform_request(request)
        return request.response

    @staticmethod
    def void_response(transaction_id: str):
        """
        Get a transaction void :class:`paynlsdk.api.transaction.voidauthorization.Response` instance

        Please note this will immediately call the API, returning the response instance

        :param transaction_id: transaction ID
        :type transaction_id: str
        :return: Transaction void response instance
        :rtype: paynlsdk.api.transaction.voidauthorization.Response
        """
        from paynlsdk.api.transaction.voidauthorization import Request
        client = APIClient()
        request = Request(transaction_id)
        client.perform_request(request)
        return request.response

    @staticmethod
    def get_banks_response():
        """
        Get a transaction getbanks :class:`paynlsdk.api.transaction.getbanks.Response` instance

        Please note this will immediately call the API, returning the response instance

        :return: Transaction getbanks response instance
        :rtype: paynlsdk.api.transaction.getbanks.Response
        """
        from paynlsdk.api.transaction.getbanks import Request
        client = APIClient()
        request = Request()
        client.perform_request(request)
        return request.response

    @staticmethod
    def get_service_response(payment_method_id: int):
        """
        Get a transaction getservice :class:`paynlsdk.api.transaction.getservice.Response` instance

        Please note this will immediately call the API, returning the response instance

        :return: Transaction getservice response instance
        :rtype: paynlsdk.api.transaction.getservice.Response
        """
        from paynlsdk.api.transaction.getservice import Request
        client = APIClient()
        request = Request(payment_method_id)
        client.perform_request(request)
        return request.response

    @staticmethod
    def get_service_payment_options_response(payment_method_id: int=None):
        """
        Get a transaction getservicepaymentoptions :class:`paynlsdk.api.transaction.getservicepaymentoptions.Response` instance

        Please note this will immediately call the API, returning the response instance

        :param payment_method_id: payment method ID
        :type payment_method_id: int
        :return: Transaction getservicepaymentoptions response instance
        :rtype: paynlsdk.api.transaction.getservicepaymentoptions.Response
        """
        from paynlsdk.api.transaction.getservicepaymentoptions import Request
        client = APIClient()
        request = Request(payment_method_id)
        client.perform_request(request)
        return request.response

    @staticmethod
    def info_response(transaction_id: str, entrance_code: str=None):
        """
        Get a transaction info :class:`paynlsdk.api.transaction.info.Response` instance

        Please note this will immediately call the API, returning the response instance

        :param transaction_id: transaction ID
        :type transaction_id: str
        :param entrance_code: entrance code
        :type entrance_code: str
        :return: Transaction info response instance
        :rtype: paynlsdk.api.transaction.info.Response
        """
        from paynlsdk.api.transaction.info import Request
        client = APIClient()
        request = Request(transaction_id, entrance_code)
        client.perform_request(request)
        return request.response

    @staticmethod
    def status_response(transaction_id: str):
        """
        Get a transaction status :class:`paynlsdk.api.transaction.status.Response` instance

        Please note this will immediately call the API, returning the response instance

        :param transaction_id: transaction ID
        :type transaction_id: str
        :return: Transaction status response instance
        :rtype: paynlsdk.api.transaction.status.Response
        """
        from paynlsdk.api.transaction.status import Request
        client = APIClient()
        request = Request(transaction_id)
        client.perform_request(request)
        return request.response

    @staticmethod
    def refund_response(transaction_id: str, amount: int=None, description: str=None, process_date: datetime=None):
        """
        Get a transaction refund :class:`paynlsdk.api.transaction.refund.Response` instance

        Please note this will immediately call the API, returning the response instance

        :param transaction_id: transaction ID
        :type transaction_id: str
        :param amount: transaction amount to refund
        :type amount: int
        :param description: refund description
        :type description: str
        :param process_date: date at which refund needs to be processed
                TODO: this *should* be a datetime
        :type process_date: str
        :return: transaction status
        :rtype: paynlsdk.api.transaction.refund.Response
        """
        from paynlsdk.api.transaction.refund import Request
        client = APIClient()
        request = Request(transaction_id, amount, description, process_date)
        client.perform_request(request)
        return request.response

    @staticmethod
    def start_response(amount: str,
              ip_address: str,
              finish_url: str,
              payment_option_id: int=None,
              payment_option_sub_id: int=None,
              transaction: TransactionData=None,
              stats_data: TransactionStartStatsData=None,
              end_user: TransactionEndUser=None,
              sale_data: SalesData=None,
              test_mode: bool=False,
              transfer_type: str=None,
              transfer_value: str=None
              ):
        """
        Get a transaction start :class:`paynlsdk.api.transaction.start.Response` instance

        Please note this will immediately call the API, returning the response instance

        :param amount: total order amount(cents)
        :type amount: int
        :param ip_address: IP address
        :type ip_address: str
        :param finish_url: URL to call when finished
        :type finish_url: str
        :param payment_option_id: The ID of the payment option (for iDEAL use 10).
        :type payment_option_id: int
        :param payment_option_sub_id: In case of an iDEAL payment this is the ID of the bank
                See the paymentOptionSubList in the getService function.
        :type payment_option_sub_id: int
        :param transaction:
        :type transaction: TransactionData
        :param stats_data:
        :type stats_data: TransactionStartStatsData
        :param end_user:
        :type end_user: TransactionEndUser
        :param sale_data:
        :type sale_data: SalesData
        :param test_mode: whether or not to perform this transaction start in TEST mode
        :type test_mode: bool
        :param transfer_type: Use transaction, merchant or alliance to change the benificiary owner of the transaction
        :type transfer_type: str
        :param transfer_value: Merchant ID (M-xxxx-xxxx) or order ID
        :type transfer_value: str
        :return: Transaction start response instance
        :rtype: paynlsdk.api.transaction.start.Response
        """
        from paynlsdk.api.transaction.start import Request
        client = APIClient()
        request = Request(amount, ip_address, finish_url, payment_option_id, payment_option_sub_id,
                          transaction, stats_data, end_user, sale_data, test_mode, transfer_type, transfer_value)
        client.perform_request(request)
        return request.response
