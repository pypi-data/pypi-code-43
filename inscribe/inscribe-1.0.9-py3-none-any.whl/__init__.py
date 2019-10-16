from ._version import __version__
from inscribe.errors import InscribeAPIException
from inscribe.pusher import PusherFactory
from requests import HTTPError
import datetime
import inscribe.config as inscribe_config
import json
import logging
import os
import requests
import urllib
import threading
import atexit

try:
    ENVIRONMENT = os.environ['INSCRIBE_PYTHON_ENV']
except KeyError:
    ENVIRONMENT = 'production'

logger = logging.getLogger("inscribe-api")
config = inscribe_config.config
MS_IN_SECOND = 1000
SECONDS_IN_AN_HOUR = 3600
TIMEOUT_MS = MS_IN_SECOND * SECONDS_IN_AN_HOUR
CHECK_QUEUE_INTERVAL = 10
DEFAULT_API_VERSION = 1
CONFIG = config[ENVIRONMENT]['api']


class Client(object):
    def __init__(self, api_key: str, user_id: str, timeout: int = TIMEOUT_MS,
                 check_queue_interval: int = CHECK_QUEUE_INTERVAL, version: int = None,
                 async_enabled: bool = False, host: str = CONFIG['url']):
        logger.info("Instantiate API class")

        self._version = version or DEFAULT_API_VERSION
        self.session = requests.Session()
        self.api_key = api_key
        self.domain_url = host
        self.user_id = user_id
        self.pusher_enabled = async_enabled

        if self.pusher_enabled is True:
            self.channel = PusherFactory(
                api_key=self.api_key,
                base_url=self.base_url,
                pusher_key=CONFIG['pusher_key'],
                user_id=self.user_id
            ).get_pusher_channel()
            self.queue = []
            self.check_queue_interval = check_queue_interval
            self._check_queue()
            atexit.register(self.stop_queue_check)

        self.timeout = timeout
        self.token = None

    def create_customer(self, customer_name: str) -> dict:
        """
        Creates a customer
        """
        url = "/customers"
        payload = {"customer_name": customer_name}
        return self._post(url, json=payload)

    def get_all_customers(self, page_number: int = 1) -> dict:
        """
        Return all available customers
        """
        url = f"/customers?customersPageNumber={page_number}"
        return self._get(url)

    def get_customer(self, customer_id: int) -> dict:
        """
        Get particular customer
        """
        url = "/customers/{customer_id}".format(customer_id=customer_id)
        return self._get(url)

    def delete_customer(self, customer_id: int) -> dict:
        """
        Delete particular customer
        """
        url = "/customers/{customer_id}".format(customer_id=customer_id)
        return self._delete(url)

    def upload_document(self, customer_id: int, document: object,
                        success_callback: object = None, error_callback: object = None):
        url = f"/customers/{customer_id}/documents"
        filename = os.path.basename(document.name)
        upload_response = self._post(url, files=((filename, document),))

        if self.pusher_enabled and (success_callback is not None) and (error_callback is not None):
            return self._manage_upload_document_response(
                upload_response,
                success_callback=success_callback,
                error_callback=error_callback
            )
        else:
            return upload_response

    def check_document(self, customer_id: int, document_id: int) -> dict:
        """
        Analyse document and returns a response with a single value `fraud_score`

        :param customer_id: id of customer folder provided in response of Create Customer
        :param document_id: id of document provided in response of Upload Document
        """

        url = f"/customers/{customer_id}/documents/{document_id}"
        return self._get(url)

    def delete_document(self, customer_id: int, document_id: int) -> dict:
        """
        Delete particular document
        """
        url = "/customers/{customer_id}/documents/{document_id}".format(
            customer_id=customer_id, document_id=document_id)
        return self._delete(url)

    def document_diff(self, customer_id, document_one_id, document_two_id):
        """
        Find differences between two documents
        """
        url = "/customers/{customer_id}/documents/diff?document_one_id={document_1}&document_two_id={document_2}".format(
            customer_id=customer_id, document_1=document_one_id, document_2=document_two_id)
        return self._get(url)

    def get_blacklist(self) -> dict:
        """
        Get user blacklist
        """
        url = "/blacklist"
        return self._get(url)

    def create_blacklist_entry(self, name: str = None, phone_number: str = None, address: str = None, file=None) -> dict:
        """
        Create a single blacklist entry
        """
        url = "/blacklist"
        payload = {"name": name, "phone_number": phone_number, "address": address, "file": file}
        return self._post(url, json=payload)

    def update_blacklist_entry(self, blacklist_id: int, name: str = None, phone_number: str = None, address: str = None) -> dict:
        """
        Update existing blacklist entry
        """
        url = "/blacklist/{blacklist_id}".format(blacklist_id=blacklist_id)
        payload = {"name": name, "phone_number": phone_number, "address": address}
        return self._post(url, json=payload)

    def delete_blacklist_entry(self, blacklist_id: int) -> dict:
        """
        Delete particular blacklist entry
        """
        url = "/blacklist/{blacklist_id}".format(blacklist_id=blacklist_id)
        return self._delete(url)

    def upload_template(self, document: object):
        url = "/templates"
        filename = os.path.basename(document.name)
        return self._post(url, files=((filename, document),))

    def get_all_templates(self) -> dict:
        url = "/templates"
        return self._get(url)

    def get_template(self, template_id: int) -> dict:
        url = "/templates/{template_id}".format(template_id=template_id)
        return self._get(url)

    def delete_template(self, template_id: int) -> dict:
        url = "/templates/{template_id}".format(template_id=template_id)
        return self._delete(url)

    @property
    def headers(self):
        return {'Authorization': self.api_key}

    @property
    def version(self):
        return "v%s" % self._version

    @property
    def base_url(self):
        return f"{self.domain_url}/api/{self.version}"

    def _manage_upload_document_response(
            self, response: dict, success_callback: object, error_callback: object):
        result_urls = response['result_urls'] if 'result_urls' in response else None

        if result_urls:
            result_url = result_urls[0]
            document_id = result_url["document_id"]
            bind_name = f"document-processed-{document_id}"
            self._add_binding_to_queue(bind_name, document_id, error_callback)
            self.channel.bind(
                bind_name,
                lambda data: self._process_pusher_message(
                    data=data,
                    bind_name=bind_name,
                    success_callback=success_callback,
                    error_callback=error_callback
                )
            )
        else:
            error_callback(
                InscribeAPIException(
                    'Could not parse output from upload document response. Please try again.'
                )
            )

    def _process_pusher_message(
            self, data: dict, bind_name: str,
            success_callback: object, error_callback: object):
        json_data = json.loads(data)
        self._find_and_remove_from_queue(bind_name)
        success_callback(self.check_document(json_data["customer_id"], json_data["document_id"]))

    def _check_queue(self):
        for index, binding in enumerate(self.queue):
            currentTimestamp = datetime.datetime.now().timestamp()
            if ((currentTimestamp - binding['started_at']) >= self.timeout):
                self._remove_from_queue(binding['bind_name'], index)
                binding['error_callback'](
                    InscribeAPIException(f"Document ({binding['document_id']}) timed out, please try again.")
                )

        self.queue_check = threading.Timer(self.check_queue_interval, self._check_queue)
        self.queue_check.daemon = True
        self.queue_check.start()

    def stop_queue_check(self):
        self.queue_check.cancel()

    def _find_and_remove_from_queue(self, bind_name: str):
        for index, binding in enumerate(self.queue):
            if binding['bind_name'] == bind_name:
                self._remove_from_queue(bind_name, index)

    def _remove_from_queue(self, bind_name: str, index: int):
        self.channel.unbind(bind_name)
        self.queue.pop(index)

    def _add_binding_to_queue(self, bind_name: str, documentId: int, error_callback: object):
        self.queue.append({
            'bind_name': bind_name,
            'document_id': documentId,
            'error_callback': error_callback,
            'started_at': datetime.datetime.now().timestamp()
        })

    def _get_http_method(self, method_name):
        http_method_mapping = {
            "GET": self.session.get,
            "POST": self.session.post,
            "DELETE": self.session.delete,
            "PUT": self.session.put,
            "PATCH": self.session.patch,
            "HEAD": self.session.head
        }

        try:
            return http_method_mapping[method_name]
        except KeyError:
            raise InscribeAPIException("HTTP method '%s' is invalid!" % method_name)

    def _get(self, url, **kwargs):
        return self._request("GET", url, **kwargs)

    def _post(self, url, **kwargs):
        return self._request("POST", url, **kwargs)

    def _delete(self, url, **kwargs):
        return self._request("DELETE", url, **kwargs)

    def _put(self, url, **kwargs):
        return self._request("PUT", url, **kwargs)

    def _patch(self, url, **kwargs):
        return self._request("PATCH", url, **kwargs)

    def _head(self, url, **kwargs):
        return self._request("HEAD", url, **kwargs)

    def _request(self, method, url, **kwargs):

        http_method = self._get_http_method(method)

        url = self.base_url + url
        logger.info("HTTP %s request. : %s " % (method, url))

        response = http_method(url, headers=self.headers, **kwargs)
        logger.info("Response: %s" % response.text)
        # print("response: "+response.text)
        try:
            response.raise_for_status()
        except HTTPError as e:
            logger.info(str(e))
            raise InscribeAPIException(
                f"{str(e)}\nError occurred during sending a request to {url}"
            )

        try:
            response_json = response.json()
        except ValueError:
            raise InscribeAPIException("Couldn't get a valid JSON from response")

        if "success" not in response_json:
            raise InscribeAPIException("API returned invalid response: %s" % response.text)

        # if not response_json["success"]:
        #     raise InscribeAPIException("Error occurred during API call: %s" % response_json.get("message"))

        return response_json

    def __del__(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
