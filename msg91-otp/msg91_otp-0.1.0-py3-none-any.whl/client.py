import httpx

from msg91_otp.country_code import CountryCode
from msg91_otp.utils import convert_response
from msg91_otp.utils import prefix_country_code


class BaseClient:
    """Base class for both OTPClient & AsyncOTPClient"""

    base_url = "https://api.msg91.com"
    otp_endpoint = "/api/sendotp.php"
    otp_retry_endpoint = "/api/retryotp.php"
    verify_otp_endpoint = "/api/verifyRequestOTP.php"

    def __init__(self, auth_key):
        self.auth_key = auth_key

    def get_otp_url(self):
        return self.base_url + self.otp_endpoint

    def get_resend_otp_url(self):
        return self.base_url + self.otp_retry_endpoint

    def get_verify_otp_url(self):
        return self.base_url + self.verify_otp_endpoint

    def get_otp_payload(self, receiver, **kwargs):
        receiver = prefix_country_code(CountryCode.INDIA, str(receiver))
        payload = {
                    "mobile": receiver,
                    "authkey": self.auth_key}

        if 'message' in kwargs:
            payload['message'] = kwargs.get('message')

        if 'sender' in kwargs:
            payload['sender'] = kwargs.get('sender')

        # otp can be supplied or let msg91 to
        # autogenerate on their side with ##OTP## placeholder in message
        if 'otp' in kwargs:
            payload['otp'] = kwargs.get('otp')
            if ('message' in payload) and ("##OTP##" in payload['message']):
                payload['message'] = payload['message'].replace('##OTP##', '')
        elif ('message' in payload) and ("##OTP##" not in payload['message']):
            payload['message'] = payload['message'].strip() + " ##OTP##"

        if 'otp_length' in kwargs:
            payload['otp_length'] = kwargs.get('otp_length')

        return payload

    def get_resend_otp_payload(self, receiver, **kwargs):
        receiver = prefix_country_code(CountryCode.INDIA, str(receiver))
        payload = {
                    "mobile": receiver,
                    "authkey": self.auth_key}
        return paylaod

    def get_verify_payload_headers(self, mobile, otp_value):
        mobile = prefix_country_code(CountryCode.INDIA, str(mobile))
        payload = {
                    "authkey": self.auth_key,
                    "mobile": mobile,
                    "otp": otp_value}
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        return (payload,  headers)


class OTPClient(BaseClient):
    """Synchronous OTP client
    Use this class for blocking request to API
    """
    def send_otp(self, receiver, **kwargs):
        """Request the Service to send OTP message to given number
        Args:
            receiver(str): 10 digit mobile number with country code of reciever

            message(str, optional): text message to send along with OTP
            sender(str, optional): the name to appear in SMS as sender
            otp (int, optional): the opt value to send, if not service will generate
            otp_length (int, optional): the length of otp. default 4, max 9
        Returns:
            a response object with status and status message
        """
        otp_url = self.get_otp_url()
        payload = self.get_otp_payload(receiver, **kwargs)
        service_response = httpx.post(otp_url, params=payload)
        _response = convert_response(service_response, identifier=receiver)
        return _response

    def resend_otp(self, receiver, **kwargs):
        """Resend OTP request
        Args:
            receiver(str): 10 digit mobile number with country code of receiver
        Returns:
            a response object with status and status message
        """
        retry_url = self.get_resend_otp_url()
        payload = self.get_resend_otp_payload(receiver, **kwargs)
        service_response = httpx.post(retry_url, params=payload)
        _response = convert_response(service_response)
        return _response

    def verify_otp(self, mobile, otp_value):
        """Request to verify OTP with given mobile number
        Args:
            mobile(str): mobile number to verify otp
            otp_value(int): the otp value to verify against
        Returns:
             a response object with status and status message
        """
        verify_url = self.get_verify_otp_url()
        payload, headers = self.get_verify_payload_headers(mobile, otp_value)
        service_response = httpx.post(verify_url, params=payload, headers=headers)
        _response = convert_response(service_response)
        return _response


class AsyncOTPClient(BaseClient):
    """Asynchronous OTP client
    Use this class for non-blocking request to API
    """
    async def send_otp(self, receiver, **kwargs):
        otp_url = self.get_otp_url()
        payload = self.get_otp_payload(receiver, **kwargs)
        async with httpx.AsyncClient() as client:
            service_response = await client.post(otp_url, params=payload)
        _response = convert_response(service_response)
        return _response

    async def resend_otp(self, receiver, **kwargs):
        retry_url = self.get_resend_otp_url()
        payload = self.get_resend_payload(receiver, **kwargs)
        async with httpx.AsyncClient() as client:
            service_response = await client.post(retry_url, params=payload)
        _response = convert_response(service_response)
        return _response

    async def verify_otp(self, mobile, otp_value):
        verify_url = self.get_verify_otp_url()
        payload, headers = self.get_verify_payload_headers(mobile, otp_value)
        async with httpx.AsyncClient() as client:
            service_response = await client.post(verify_url, params=payload, headers=headers)
        _response = convert_response(service_response)
        return _response
