""" This file exposes endpoints from the SWS License Service
"""

from sws_py_sdk.service import Service


class License(Service):
    def __init__(self, sws):
        super().__init__(sws)
        self.service_uri = sws.service_uris['license']

    def get_licenses(self, app_name=None, app_version=None, term=None, include_upgraded=None, include_deleted=None):
        """
        Gets the licenses owned by the user.

        :param str app_name: Use to filter by app name e.g. 'serato_studio'.
        :param str app_version: Use to filter by app version e.g. "1.9.2"
        :param str term : Use to filter by term e.g. 'permanent', 'subscription' etc.
        :param str include_upgraded: If set to 'true', will only return licenses that are upgraded.
                                     Valid values are 'true' and 'false'.
        :param str include_deleted: If set to 'true', will only return licenses that are deleted.
                                    Valid values are 'true' and 'false'. Requires 'user-license-admin' scope.
        :return: Licenses owned by the user.
        :rtype: requests.Response
        """
        return self.fetch(
            auth='bearer',
            endpoint='/api/v1/me/licenses' if self.sws.user_id == 0 else f'/api/v1/users/{self.sws.user_id}/licenses',
            body={
                'app_name': app_name,
                'app_version': app_version,
                'term': term,
                'include_upgraded': include_upgraded,
                'include_deleted': include_deleted
            }
        )

    def create_license_authorization(self,
                                     action,
                                     app_name,
                                     app_version,
                                     host_machine_id,
                                     host_machine_name,
                                     license_id,
                                     system_time):
        """
        Create a new license authorization for a host.

        :param str action: One of 'activate' or 'deactivate'.
        :param str app_name: Name of the app to authorize. E.g. 'serato_studio'.
        :param str app_version: Version of app in format 'major.minor.patch.'.
        :param str host_machine_id: Machine ID of the host.
        :param str host_machine_name: Name of host machine.
        :param str license_id: ID of the license to authorize.
        :param str system_time: Current Date/time of the client system expressed in ISO 8601 format.
        :return: a list of all licenses whose current authorization state on the host is activated,
                 and includes the RLM license file content for each activated license. The list can
                 be empty in the case that the authorization action is deactivate and no licenses
                 are authorized on the host
        :rtype: requests.Response
        """
        return self.fetch(
            method='POST',
            endpoint='/api/v1/me/licenses/authorizations' if self.sws.user_id == 0
            else f'/api/v1/users/{self.sws.user_id}/licenses/authorizations',
            auth='bearer',
            headers={'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'},
            body={
                'action': action,
                'app_name': app_name,
                'app_version': app_version,
                'host_machine_id': host_machine_id,
                'host_machine_name': host_machine_name,
                'license_id': license_id,
                'system_time': system_time
            }
        )

    def update_license_authorization(self, authorization_id, status_code):
        """
        Update the status of a license authorization action.

        :param int authorization_id: The authorization to update.
        :param int status_code: 0 is success, non-zero values are application specific.
        :return: HTTP response.
        :rtype: requests.Response
        """
        return self.fetch(
            method='PUT',
            endpoint=f'/api/v1/me/licenses/authorizations/{authorization_id}' if self.sws.user_id == 0
            else f'/api/v1/users/{self.sws.user_id}/licenses/authorizations/{authorization_id}',
            auth='bearer',
            headers={'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'},
            body={'status_code': status_code}
        )

    def get_products(self,
                     app_name=None,
                     app_version=None,
                     term=None,
                     show_license_activations=None,
                     include_upgraded=None,
                     include_deleted=None):
        """
        Gets products owned by the user.

        :param str app_name: Used to filter by app name e.g. "serato_studio".
        :param str app_version: Used to filter by app version e.g. "1.9.2".
        :param str term: Used to filter by term. E.g. 'permanent', 'subscription' etc.
        :param str show_license_activations: Returns activations for licenses if the parameter is set to true.
                                             Valid values are true or false.
        :param str include_upgraded: Return all the products include those have the upgrade_to field is not empty
                                     if the parameter is set to true. Valid values are true or false.
        :param str include_deleted: Return all the products that are deleted if the parameter is set to true.
                                    This requires user-license-admin scope. Valid values are true or false.
        :return: List of products owned by user.
        :rtype: requests.Response
        """
        return self.fetch(
            endpoint='/api/v1/me/products' if self.sws.user_id == 0 else f'/api/v1/users/{self.sws.user_id}/products',
            auth='bearer',
            body={
                'app_name': app_name,
                'app_version': app_version,
                'term': term,
                'show_license_activations': show_license_activations,
                'include_upgraded': include_upgraded,
                'include_deleted': include_deleted
            }
        )

    def add_product(self, host_machine_id=None, product_type_id=None, product_serial_number=None):
        """
        Adds a product to the user.

        :param str host_machine_id: Host physical machine id. Required when `product_type_id` is trial product.
        :param int product_type_id: Product type id. One of `product_type_id` or `product_serial_number` is required.
        :param str product_serial_number: Product serial number. One of `product_type_id` or `product_serial_number` is
                                          required.
        :return: Information on product added.
        :rtype: requests.Response
        """
        return self.fetch(
            method='POST',
            endpoint='/api/v1/me/products' if self.sws.user_id == 0 else f'/api/v1/users/{self.sws.user_id}/products',
            auth='bearer',
            body={
                'host_machine_id': host_machine_id,
                'product_type_id': product_type_id,
                'product_serial_number': product_serial_number
            }
        )

    def update_product(self, product_id, ilok_user_id):
        """
        Updates a product owned by the user.

        :param str product_id: Id of the product to update.
        :param str ilok_user_id: iLok user ID.
        :return: Information on product updated.
        :rtype: requests.Response
        """
        return self.fetch(
            method='PUT',
            endpoint=f'/api/v1/me/products/{product_id}' if self.sws.user_id == 0
            else f'/api/v1/users/{self.sws.user_id}/products/{product_id}',
            auth='bearer',
            body={'ilok_user_id': ilok_user_id}
        )

    def get_product_types(self, app_name=None, app_version=None, term=None):
        """
        Get a list of software product types.

        :param str app_name: Use to filter by app name e.g. "serato_studio".
        :param str app_version: Use to filter by app version e.g. "1.9.2".
        :param str term: Use to filter by license term. E.g. "permanent", "subscription" etc.
        :return: List of software product types.
        :rtype: requests.Response
        """
        return self.fetch(
            endpoint='/api/v1/products/types',
            auth='bearer',
            body={'app_name': app_name, 'app_version': app_version, 'term': term }
        )

    def get_product_type_details(self, product_type_id):
        """
        Get detailed product type information including a list of license types delivered by the product type.

        :param int product_type_id: Product type ID to get details for.
        :return: Detailed information on the product e.g. license types, trial reset dates etc.
        :rtype: requests.Response
        """
        return self.fetch(
            endpoint=f'/api/v1/products/types/{product_type_id}',
            auth='bearer'
        )

    def reset_trials_for_product_type(self, product_type_id, reset_date):
        """
        Reset trials for a product type.

        NOTE: requires `app-license-admin` scope.

        :param int product_type_id: The product ID for the product to reset trials for.
        :param str reset_date: Trial reset date, expressed as timestamp in ISO 8601 format
        :return:
        :rtype: requests.Response
        """
        return self.fetch(
            method='POST',
            endpoint=f'/api/v1/products/types/{product_type_id}/trialresets',
            auth='bearer',
            headers={'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'},
            body={'reset_date': reset_date}
        )

    def admin_get_products(self, checkout_order_id=None, magento_order_id=None, user_id=None):
        """
        Get a list of products filtered by purchase reference information and/or user ID.

        NOTE: requires `app-license-admin` scope.

        :param int checkout_order_id: Serato checkout order ID.
        :param int magento_order_id: Magento checkout ID.
        :param int user_id: User ID.
        :return: List of products.
        :rtype: requests.Response
        """
        return self.fetch(
            endpoint='/api/v1/products/products',
            auth='bearer',
            body={'checkout_order_id': checkout_order_id, 'magento_order_id': magento_order_id, 'user_id': user_id}
        )

    def admin_add_product(self,
                          product_type_id,
                          user_id=None,
                          user_email_address=None,
                          reseller_name=None,
                          created_by_user_id=None,
                          nfr=None,
                          notes=None,
                          valid_to=None,
                          checkout_order_id=None,
                          checkout_order_item_id=None,
                          magento_order_id=None,
                          magento_order_item_id=None,
                          subscription_status=None):
        """
        Create a new product and it's licenses with the provided purchase reference and customer reference information.

        Only permanent, timelimited and subscription license product types are supported. trial license product types
        are not supported.

        NOTE 1: One of user_id, user_email_address or reseller_name is required.
        NOTE 2: When creating a NFR license, `created_by_user_id`, `notes`, `user_id` or `user_email_address` must be
        specified.
        NOTE 3: When ordered through Serato Checkout, `checkout_order_id` and `checkout_order_item_id` must be
        specified.
        NOTE 4: When ordered through Magento, `magento_order_id` and `magento_order_item_id` must be specified.
        NOTE 5: requires `app-license-admin` scope.

        :param int product_type_id: Product type ID.
        :param int user_id:  User ID to assign to the product.
        :param str user_email_address: User email to assign to the product when user does not currently have an account.
        :param str reseller_name: Name of reseller who purchased the products
        :param str created_by_user_id: Serato created by User ID to assign through an NFR License.
        :param boolean nfr: Serato NFR state.
        :param str notes: Serato notes to explain the reason of this NFR License.
        :param str valid_to: Date at which the licenses associated with the product expire, in ISO 8601 format.
                             Required when product type is of term subscription
        :param int checkout_order_id: Serato Checkout Order ID.
        :param int checkout_order_item_id: Serato Checkout Order Item ID.
        :param int magento_order_id: Magento Order ID.
        :param int magento_order_item_id: Magento Order Item ID.
        :param str subscription_status: Subscription status is required if product is a subscription.
                                        Valid values are 'Active', 'Canceled', 'Expired', 'Past Due', 'Pending' and
                                        'Expiring'.
        :return: Information on the product added.
        :rtype: requests.Response
        """
        return self.fetch(
            method='POST',
            endpoint='/api/v1/products/products',
            auth='bearer',
            headers={'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'},
            body={
                'product_type_id': product_type_id,
                'user_id': user_id,
                'user_email_address': user_email_address,
                'reseller_name': reseller_name,
                'created_by_user_id': created_by_user_id,
                'nfr': nfr,
                'notes': notes,
                'valid_to': valid_to,
                'checkout_order_id': checkout_order_id,
                'checkout_order_item_id': checkout_order_item_id,
                'magento_order_id': magento_order_id,
                'magento_order_item_id': magento_order_item_id,
                'subscription_status': subscription_status
            }
        )

    def admin_update_product(self,
                             product_id,
                             valid_to=None,
                             checkout_order_id=None,
                             checkout_order_item_id=None,
                             magento_order_id=None,
                             magento_order_item_id=None,
                             subscription_status=None):
        """
        Update a product.

        NOTE 1: requires `app-license-admin` scope.
        NOTE 2: When product is ordered through Serato Checkout, `checkout_order_id` and `checkout_order_item_id` must
        be specified.
        NOTE 3: When product is ordered through Magento, `magento_order_id` and `mangeto_order_item_id` must be
        specified.

        :param str product_id: Product ID to update.
        :param str valid_to: Date at which the licenses associated with the product expire, in ISO 8601 format
        :param int checkout_order_id: Serato Checkout Order ID.
        :param int checkout_order_item_id: Serato Checkout Order Item ID.
        :param int magento_order_id: Magento Order ID.
        :param int magento_order_item_id: Magento Order Item ID.
        :param str subscription_status: Subscription status for a subscription product. Valid values are 'Active',
                                        'Canceled', 'Expired', 'Past Due', 'Pending' and 'Expiring'.
        :return: Information on product updated.
        :rtype: requests.Response
        """
        return self.fetch(
            method='PUT',
            endpoint=f'/api/v1/products/products/{product_id}',
            auth='bearer',
            headers={'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'},
            body={
                'valid_to': valid_to,
                'checkout_order_id': checkout_order_id,
                'checkout_order_item_id': checkout_order_item_id,
                'magento_order_id': magento_order_id,
                'magento_order_item_id': magento_order_item_id,
                'subscription_status': subscription_status
            }
        )

    def delete_product(self, product_id):
        """
        Deletes a product.

        NOTE: requires `app-license-admin` scope.

        :param str product_id: Product ID to delete.
        :return: HTTP response. 204 is successful.
        :rtype: requests.Response
        """
        return self.fetch(
            method='DELETE',
            endpoint=f'/api/v1/products/products/{product_id}',
            auth='bearer'
        )

    def get_product_info(self, product_id):
        """
        View product information.

        NOTE: requires `app-license-admin` scope.

        IMPORTANT: Will return information about deleted products.
        :param str product_id: Product ID view information for.
        :return: Information on product.
        :rtype: requests.Response
        """
        return self.fetch(
            endpoint=f'/api/v1/products/products/{product_id}',
            auth='bearer'
        )
