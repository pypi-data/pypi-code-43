import sys
from unittest import TestCase
from datetime import timedelta, datetime
import random
from tingg.adapters import TinggAdapter


class TinggAdapterTestCase(TestCase):
    adapter = TinggAdapter(iv_key='FH3Jr2qx464rtyt',
                           secret_key='rcn2y9P6546xC',
                           service_code='TEST66314',
                           access_key='$2a$08$xxDfOWLb1xx54353.P5dUxxxxxypMJaGI08S',
                           domain='sandbox'
                           )
    due_date = (datetime.now() + timedelta(days=0, hours=-3, minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
    merchant_transaction_id = random.randint(0, sys.maxunicode)

    def test_service_code_is_string(self):
        """
        Test if service code is string and is not null
        :return:
        """
        self.assertEqual(self.adapter.service_code, 'TEST66314')

    def test_checkout_encryption(self):
        """
        Test if the encryption is not empty on null
        :return:
        """
        response = self.adapter.get_encryption(
            msisdn='07000000000',
            transaction_id=self.merchant_transaction_id,
            account_number=self.merchant_transaction_id,
            amount='2000',
            currency_code='KES',
            country_code='KE',
            description='Testing QA',
            due_date=self.due_date,
            callback_url='',
            customer_first_name='Test',
            customer_last_name='QA',
            customer_email='qa@test.com',
            checkout_type='modal',
            payer_client_code='',
            language_code='en',
            success_url='',
            fail_url=''
        )

        assert response is not None

    def test_with_no_checkout_type(self):
        """
        This function should check if no checkout type defaults to express
        :return:
        """
        response = self.adapter.get_encryption(
            msisdn='07000000000',
            transaction_id=self.merchant_transaction_id,
            account_number=self.merchant_transaction_id,
            amount='2000',
            currency_code='KES',
            country_code='KE',
            description='Testing QA',
            due_date=self.due_date,
            callback_url='',
            customer_first_name='Test',
            customer_last_name='QA',
            customer_email='qa@test.com',
            checkout_type='',
            payer_client_code='',
            language_code='en',
            success_url='',
            fail_url=''
        )

        assert 'express' in response

    def test_staging_domain_with_all_lower_case(self):
        """
        Test if the function accepts redirects to staging when user uses lower case
        :return:
        """
        adapter = TinggAdapter(iv_key='FH3Jr2qx464rtyt',
                               secret_key='rcn2y9P6546xC',
                               service_code='TEST66314',
                               access_key='$2a$08$xxDfOWLb1xx54353.P5dUxxxxxypMJaGI08S',
                               domain='staging'
                               )
        response = adapter.get_encryption(
            msisdn='07000003430',
            transaction_id=self.merchant_transaction_id,
            account_number=self.merchant_transaction_id,
            amount='2000',
            currency_code='KES',
            country_code='KE',
            description='Testing QA',
            due_date=self.due_date,
            callback_url='',
            customer_first_name='Test',
            customer_last_name='QA',
            customer_email='qa@test.com',
            checkout_type='',
            payer_client_code='',
            language_code='en',
            success_url='',
            fail_url=''
        )
        self.assertTrue('9001' in str(response))

    def test_staging_domain_with_all_upper_case(self):
        """
        Test if the function accepts redirects to staging when user uses lower case
        :return:
        """
        adapter = TinggAdapter(iv_key='FH3Yr2qx464rtyt',
                               secret_key='rcn2y9P6546xC',
                               service_code='TEST66314',
                               access_key='$2a$08$xxDfOWLb1xx54353.P5dUxxxxxypMJaGI08S',
                               domain='STAGING'
                               )
        response = adapter.get_encryption(
            msisdn='070002333430',
            transaction_id=self.merchant_transaction_id,
            account_number=self.merchant_transaction_id,
            amount='2000',
            currency_code='KES',
            country_code='KE',
            description='Testing QA',
            due_date=self.due_date,
            callback_url='',
            customer_first_name='Test',
            customer_last_name='QA',
            customer_email='qa@test.com',
            checkout_type='',
            payer_client_code='',
            language_code='en',
            success_url='',
            fail_url=''
        )
        self.assertTrue('9001' in str(response))

    def test_checkout_with_no_domain(self):
        """
        This test should default to staging
        :return:
        """
        domain_adapter = TinggAdapter(iv_key='FH3Jr2qx464rtyt',
                                      secret_key='rcn2y9P6546xC',
                                      service_code='TESU66314',
                                      access_key='$2a$08$xxDfOWLb1xx54353.P5dUxxxxxypMJaGI08S',
                                      domain='SANDBOX'
                                      )

        no_domain_response = domain_adapter.get_encryption(
            msisdn='070003400767',
            transaction_id=self.merchant_transaction_id,
            account_number=self.merchant_transaction_id,
            amount='2000',
            currency_code='KES',
            country_code='KE',
            description='Testing QA',
            due_date=self.due_date,
            callback_url='',
            customer_first_name='Test',
            customer_last_name='QA',
            customer_email='qa@test.com',
            checkout_type='',
            payer_client_code='',
            language_code='en',
            success_url='',
            fail_url=''
        )
        assert '9001' in str(no_domain_response)
