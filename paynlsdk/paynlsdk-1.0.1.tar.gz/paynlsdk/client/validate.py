from paynlsdk.api.client import APIClient


class Validate(object):
    @staticmethod
    def pay_server_ip(ip_address: str):
        """
        Validate a Pay server IP

        :param ip_address: IP address
        :type ip_address: str
        :return: Request instance
        :rtype: paynlsdk.api.validate.payserverip.Request
        """
        response = Validate.pay_server_ip_response(ip_address)
        return response.result

    @staticmethod
    def pay_server_ip_request():
        """
        Get a Pay server IP validation :class:`paynlsdk.api.validate.payserverip.Request` instance

        :return: Request instance
        :rtype: paynlsdk.api.validate.payserverip.Request
        """
        from paynlsdk.api.validate.payserverip import Request
        request = Request()
        return request

    @staticmethod
    def pay_server_ip_response(ip_address: str):
        """
        Get a Pay server IP validation :class:`paynlsdk.api.validate.payserverip.Response` instance

        :param ip_address: IP address
        :type ip_address: str
        :return: Response instance
        :rtype: paynlsdk.api.validate.payserverip.Response
        """
        from paynlsdk.api.validate.payserverip import Request
        client = APIClient()
        request = Request(ip_address)
        client.perform_request(request)
        return request.response

