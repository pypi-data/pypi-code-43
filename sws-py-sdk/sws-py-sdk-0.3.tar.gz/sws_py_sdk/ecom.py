""" This file exposes endpoints from the SWS Ecom Service
"""

from requests.auth import HTTPBasicAuth

from sws_py_sdk.service import Service

class Ecom(Service):

    def __init__(self, sws):
        super().__init__(sws)
        self.service_uri = sws.service_uris['ecom']

    def add_payment_method(self, nonce=None, device_data=None, billing_address_id=None):
        """ Add a payment method to the authenticated client user.
            nonce: str
                One-time-use reference to payment information provided by the user.
            device_data: str
                User device information.
            billing_address_id: str
                The two-letter value for an address associated with a specific customer ID.
        """
        return self.fetch(
            auth='bearer',
            endpoint='/api/v1/me/paymentmethods' if self.sws.user_id == 0 else '/api/v1/users/' +
                str(self.sws.user_id) + '/paymentmethods',
            body={"nonce": nonce, "device_data": device_data, "billing_address_id": billing_address_id },
            method='POST'
        )

    def add_plan_change_request(self, subscription_id, catalog_product_id):
        """ Create a new plan change that belongs to the authenticated client user.

            subscription_id: int
                Id of the subscription that is requesting change
            catalog_product_id: int
                The id of the product that the subscription wants to change to
        """
        endpoint = '/api/v1/me/' if self.sws.user_id == 0 else '/api/v1/users/' + str(self.sws.user_id)
        endpoint = endpoint + "subscriptions/" + subscription_id + "/planchanges"

        return self.fetch(
            auth='bearer',
            endpoint=endpoint,
            body={"catalog_product_id": catalog_product_id},
            method='POST'
        )

    def get_subscriptions(self, subscription_id=''):
        """ Get subscriptions owned by a user
        """
        endpoint = "/api/v1/me/subscriptions" if self.sws.user_id == 0 else "/api/v1/users/" + str(self.sws.user_id) + "/subscriptions"
        if subscription_id != '':
            endpoint += "/" + str(subscription_id)
        return self.fetch(
            auth="bearer",
            endpoint=endpoint,
            method="GET"
        )
        

    def get_invoices(self, order_id):
        """ Get list of all invoices for a user

            order_id: int
                ID of order
        """
        endpoint = "/api/v1/me" if self.sws.user_id == 0 else "/api/v1/users/" + str(self.sws.user_id)
        endpoint = endpoint + "/orders/" + str(order_id) + "/invoice" 
        return self.fetch(
            auth="bearer",
            endpoint=endpoint,
            method="GET"
        )

    def get_orders(self, order_id=0):
        """ Get list of all orders created by the authenticated client user

            order_id: int
                ID of order
        """
        endpoint = "/api/v1/me" if self.sws.user_id == 0 else "/api/v1/users/" + str(self.sws.user_id)
        endpoint = endpoint + "/orders"
        if order_id != 0:
            endpoint = endpoint + "/" + str(order_id)
        return self.fetch(
            auth="bearer",
            endpoint=endpoint,
            method="GET"
        )

    def get_payment_methods(self):
        """ Gets users payment methods
        """
        endpoint = '/api/v1/me' if self.sws.user_id == 0 else '/api/v1/users/' + str(self.sws.user_id)
        endpoint += '/paymentmethods'
        
        return self.fetch(
            auth='bearer',
            endpoint=endpoint,
            method='GET'
        )
        

    def update_payment_methods(self, payment_token, nonce, device_data=None, billing_address_id=None):
        """ Update the payment method that belongs to the user

            payment_token: str
                Payment token string relating to user's payment method
            nonce: str
                One-time-use reference to payment information provided by the user.
            device_data: str
                User device information.
            billing_address_id: str
                The two-letter value for an address associated with a specific customer ID. 
        """
        endpoint = '/api/v1/me/paymentmethods/' if self.sws.user_id == 0 else '/api/v1/users/' + str(self.sws.user_id) + '/paymentmethods/'
        endpoint = endpoint + payment_token

        return self.fetch(
            auth='bearer',
            endpoint=endpoint,
            method='PUT',
            body={ "nonce": nonce, "device_data": device_data, "billing_address_id": billing_address_id }
        )
    def update_plan_change(self, subscription_id, plan_change_id):
        """ Update an existing plan change

            subscription_id: str
                Subscripton ID
            plan_change_id: str
                The ID for the change request
        """
        endpoint = '/api/v1/me' if self.sws.user_id == 0 else '/api/v1/users/' + str(self.sws.user_id)
        endpoint = endpoint + "/subscriptions/" + subscription_id + "/planchanges/" + plan_change_id
        return self.fetch(
            auth="bearer",
            endpoint=endpoint,
            method="PUT"
        )

    def update_subscription(self, subscription_id, number_of_billing_cycle=None, payment_method_token=None):
        """ Update a subscription owned by the user

            subscription_id: str
                Subscripton ID
            number_of_billing_cycle: int
                Number of billing cyles after which the subscription will expire.
            payment_method_token: str
                Token style identifier of the payment method
        """
        endpoint = '/api/v1/me' if self.sws.user_id == 0 else '/api/v1/users/' + str(self.sws.user_id)
        endpoint = endpoint + "/subscriptions/" + subscription_id
        return self.fetch(
            auth="bearer",
            endpoint=endpoint,
            body={"number_of_billing_cycle": number_of_billing_cycle, "payment_method_token": payment_method_token},
            method="PUT"
        )

    def delete_payment_method(self, payment_method_token):
        """ Deletes the user's payment method for the given payment method token

            payment_method_token: str
                Token style identifier of the payment method
        """
        endpoint = endpoint = '/api/v1/me' if self.sws.user_id == 0 else '/api/v1/users/' + str(self.sws.user_id)
        endpoint = endpoint + "/paymentmethods/" + payment_method_token
        return self.fetch(
            auth="bearer",
            endpoint=endpoint,
            method="DELETE"
        )

    def delete_subscription(self, subscription_id):
        """ Deletes the user's subscription for the given subscription id

            subscription_id: int
                Token style identifier of the payment method
        """
        endpoint = endpoint = '/api/v1/me' if self.sws.user_id == 0 else '/api/v1/users/' + str(self.sws.user_id)
        endpoint = endpoint + "/subscriptions/" + subscription_id
        return self.fetch(
            auth="bearer",
            endpoint=endpoint,
            method="DELETE"
        )
