import sys
import json
from datetime import timedelta, datetime

from utils.Encryption import Encryption


class TinggAdapter(object):
    STAGING_URL = 'https://beep2.cellulant.com:9001'
    SANDBOX_URL = 'https://beep2.cellulant.com:9212'

    DEFAULT_PATH = '/checkout/v2/'

    def __init__(self, iv_key, secret_key, service_code, access_key, domain):
        self.iv_key = iv_key
        self.secret_key = secret_key
        self.service_code = service_code
        self.access_key = access_key

        # Making a dictionary for checkout environments
        sandbox_dic = ['Sandbox', 'SANDBOX', 'SandBox', 'sandbox']
        staging_dic = ['STAGING', 'Staging', 'staging']
        if str(domain) in sandbox_dic:
            self.domain = self.SANDBOX_URL
        elif str(domain) in staging_dic:
            self.domain = self.STAGING_URL
        else:
            self.domain = self.STAGING_URL

    def get_encryption(self, msisdn='',
                       transaction_id='',
                       account_number='',
                       amount='',
                       currency_code='KES',
                       country_code='KE',
                       description='',
                       due_date='',
                       callback_url='',
                       customer_first_name='',
                       customer_last_name='',
                       customer_email='',
                       checkout_type='',
                       payer_client_code='',
                       language_code='',
                       success_url='',
                       fail_url=''
                       ):
        if due_date is None:
            # set due date for tomorrow by default.
            due_date = (datetime.now() + timedelta(days=0, hours=-3, minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(due_date, int):
            due_date = (datetime.now() + timedelta(days=0, hours=-3, minutes=int(due_date))).strftime(
                '%Y-%m-%d %H:%M:%S')

        if not checkout_type:
            # set express as default.
            checkout_type = 'express'

        payload = {
            "merchantTransactionID": transaction_id,
            "accountNumber": account_number,
            "customerFirstName": customer_first_name,
            "customerLastName": customer_last_name,
            "MSISDN": msisdn,
            "customerEmail": customer_email,
            "requestAmount": amount,
            "currencyCode": currency_code,
            "serviceCode": self.service_code,
            "dueDate": due_date,
            "requestDescription": description,
            "countryCode": country_code,
            "paymentWebhookUrl": callback_url,
            "payerClientCode": payer_client_code,
            "languageCode": language_code,
            "successRedirectUrl": success_url,
            "failRedirectUrl": fail_url
        }
        # Initiate encryption
        cypher = Encryption(iv_=self.iv_key, key=self.secret_key)

        # The following function will encrypt all the params provided with iv and secret key
        encrypted_params = cypher.encrypt(json.dumps(payload))

        # The following function will return the url for checkout

        checkout_page = "{}{}{}/?params={}&accessKey={}&countryCode={}".format(
            self.domain,
            self.DEFAULT_PATH,
            checkout_type,
            encrypted_params,
            self.access_key,
            country_code)
        return checkout_page
