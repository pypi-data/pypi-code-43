from django.conf import settings
from django.utils import timezone

from Crypto.Hash import SHA512
from zeep import Client

from . import exceptions


class PayCometClient:
    wsdl = "https://api.paycomet.com/gateway/xml-bankstore?wsdl"

    def __init__(self):
        self.client = Client(wsdl=self.wsdl)
        self.merchant_code = settings.PAYCOMET_MERCHANT_CODE
        self.terminal = settings.PAYCOMET_TERMINAL
        self.password = settings.PAYCOMET_PASSWORD
        self.jet_id = settings.PAYCOMET_JET_ID

    def create_payment(self, request, pay_tpv_token, amount):
        ip = self._get_client_ip(request)
        id_user, token_user = self.add_user_token(pay_tpv_token, ip)
        return self.execute_purchase(id_user, token_user, amount, ip)

    def add_user_token(self, pay_tpv_token, ip):
        signature = self._get_sha512_signature(
            f"{self.merchant_code}{pay_tpv_token}{self.jet_id}{self.terminal}{self.password}"
        )

        params = {
            'DS_MERCHANT_MERCHANTCODE': self.merchant_code,
            'DS_MERCHANT_TERMINAL': self.terminal,
            'DS_MERCHANT_JETTOKEN': pay_tpv_token,
            'DS_MERCHANT_JETID': self.jet_id,
            'DS_MERCHANT_MERCHANTSIGNATURE': signature,
            'DS_ORIGINAL_IP': ip,
        }

        response = self.client.service.add_user_token(**params)

        self._check_response_error(response)

        return response['DS_IDUSER'], response['DS_TOKEN_USER']

    def execute_purchase(self, id_user, token_user, amount, ip):
        date = timezone.now().strftime("%Y/%m/%d %H:%M:%S")
        order = f"MERCHANTORDER-{date}"
        signature = self._get_sha512_signature(
            f"{self.merchant_code}{id_user}{token_user}"
            f"{self.terminal}{amount}{order}{self.password}"
        )

        product_description = "XML_BANKSTORE TEST product_description"
        owner = "XML_BANKSTORE TEST owner"

        params = {
            'DS_MERCHANT_MERCHANTCODE': self.merchant_code,
            'DS_MERCHANT_TERMINAL': self.terminal,
            'DS_IDUSER': id_user,
            'DS_TOKEN_USER': token_user,
            'DS_MERCHANT_AMOUNT': amount,
            'DS_MERCHANT_ORDER': order,
            'DS_MERCHANT_CURRENCY': 'EUR',
            'DS_MERCHANT_MERCHANTSIGNATURE': signature,
            'DS_ORIGINAL_IP': ip,
            'DS_MERCHANT_PRODUCTDESCRIPTION': product_description,
            'DS_MERCHANT_OWNER': owner,
            'DS_MERCHANT_SCORING': '',
            'DS_MERCHANT_DATA': '',
            'DS_MERCHANT_MERCHANTDESCRIPTOR': '',
            'DS_MERCHANT_SCA_EXCEPTION': '',
            'DS_MERCHANT_TRX_TYPE': '',
            'DS_ESCROW_TARGETS': '',
            'DS_USER_INTERACTION': '',
        }

        response = self.client.service.execute_purchase(**params)

        self._check_response_error(response)

        return response

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    @staticmethod
    def _get_sha512_signature(code):
        return SHA512.new(code.encode('utf-8')).hexdigest()

    @staticmethod
    def _check_response_error(response):
        error = response['DS_ERROR_ID']
        if error not in [0, '0']:
            raise exceptions.PaymentError(
                f"Se ha producido un error: Código {error}"
            )
