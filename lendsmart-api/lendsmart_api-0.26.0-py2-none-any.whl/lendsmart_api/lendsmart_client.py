from __future__ import absolute_import

import json
import logging
from datetime import datetime
import time
import pkg_resources
import requests

from lendsmart_api.errors import ApiError, UnexpectedResponseError
from lendsmart_api.objects import PredictionChunk, PredictionWorkflow, PredictionSegment, Document, Base, LoanApplication, AccountSign
from lendsmart_api.objects.filtering import Filter

from .common import load_and_validate_keys, SSH_KEY_TYPES
from .paginated_list import PaginatedList

package_version = pkg_resources.require("lendsmart_api")[0].version

logger = logging.getLogger(__name__)


class Group:
    def __init__(self, client):
        self.client = client

class PredictionGroup(Group):
    def chunks(self, *filters):
        """
        Requests and returns a list of PredictionChunk on your
        account.
        """
        return self.client._get_and_filter(PredictionChunk, *filters)

    def chunk_create(self, label=None):
        """
        Creates a new PredictionChunk, with given inputs.

        :param label: The label for the new client.  If None, a default label based
            on the new client's ID will be used.

        :returns: A new PredictionChunk

        :raises ApiError: If a non-200 status code is returned
        :raises UnexpectedResponseError: If the returned data from the api does
            not look as expected.
        """
        result = self.client.post('/prediction_chunks', data=label)

        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating Prediction Chunk '
                                          'Client!', json=result)
        c = PredictionChunk(self.client, result['id'], result)
        print("Prediction id %s " % c.id)
        print("Prediction name %s " % c.object_meta.name)
        return c

    def segment_create(self, label=None):
        """
        Creates a new PredictionSegments, with given inputs.

        :param label: The label for the new client.  If None, a default label based
            on the new client's ID will be used.

        :returns: A new PredictionSegments

        :raises ApiError: If a non-200 status code is returned
        :raises UnexpectedResponseError: If the returned data from the api does
            not look as expected.
        """
        result = self.client.post('/prediction_segments', data=label)

        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating Prediction Segment '
                                          'Client!', json=result)
        print("client result :", result)

        c = PredictionSegment(self.client, result['id'], result)
        return c

    def workflows(self, *filters):
        """
        Requests and returns a list of PredictionWorkflow on your
        account.
        """
        return self.client._get_and_filter(PredictionWorkflow, *filters)

    def workflow_create(self, data=None):
        """
        Creates a new PredictionWorkflow, with given inputs.

        :param label: The label for the new client.  If None, a default label based
            on the new client's ID will be used.

        :returns: A new PredictionWorkflow

        :raises ApiError: If a non-200 status code is returned
        :raises UnexpectedResponseError: If the returned data from the api does
            not look as expected.
        """
        result = self.client.post('/prediction_workflows', data=data)

        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating Longivew '
                                          'Client!', json=result)

        c = PredictionWorkflow(self.client, result['id'], result)
        return c

    def loan_document_create(self, data=None):
        """
        Creates a new PredictionWorkflow, with given inputs.

        :param label: The label for the new client.  If None, a default label based
            on the new client's ID will be used.

        :returns: A new PredictionWorkflow

        :raises ApiError: If a non-200 status code is returned
        :raises UnexpectedResponseError: If the returned data from the api does
            not look as expected.
        """
        result = self.client.post('/loan_documents', data=data)

        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating LoanApplication'
                                          'Client!', json=result)

        c = LoanApplication(self.client, result['id'], result)
        return c

class Documents(Group):
    def documents(self, *filters):
        """
        Requests and returns a list of Document on your
        account.
        """
        return self.client._get_and_filter(Document, *filters)

    def document_get(self, label=None):
        """
        Get a Document

        :returns: The Document.
        :rtype: Document
        """
        result = self.client.get('/documents/{}'.format(label))
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when getting Document'
                                          'Client!', json=result)
        print("client result :", result)
        c = Document(self.client, result['id'], result)
        return c

    def document_update_status(self, did=None, updated_at=None, param=None):
        """
        Update a Document status

        :returns: The Document.
        :rtype: Document
        """
        current_time = time.time()
        result = self.client.put('/documents/{}/status?updated_at={}'.format(did, updated_at), data=param)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when updating Document'
                                          'Client!', json=result)
        print("client result :", result)
        c = Document(self.client, result['id'], result)
        return c

class AccountSignGroup(Group):
    def account_sign_update(self, id, param=None):
        """
        Update a AccountSign

        :returns: The Updated AccountSign.
        :rtype: AccountSign
        """
        result = self.client.put('/account_signs/{}'.format(id), data=param)
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when getting AccountSign'
                                          'Client!', json=result)
        print("client result updated response:\n", result)

    def signature_get(self, label=None):
        """
        Get a Signature

        :returns: The Signature.
        :rtype: Signature
        """
        result = self.client.get('/account_signs/{}'.format(label))
        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when getting Signature'
                                          'Client!', json=result)
        print("signature {} get client response:".format(label), result)
        c = AccountSign(self.client, result['id'], result)
        return result

class LendsmartClient:
    def __init__(self, service_account, base_url, user_agent=None):
        """
        The main interface to the Lendsmart API.

        :param service_account: The service_account is used for communication with the
                      API.  Can be either a Lambda servie account or other.
        :type service_account: ServiceAccount
        :param base_url: The base URL for API requests.  Generally, you shouldn't
                         change this.
        :type base_url: str
        :param user_agent: What to append to the User Agent of all requests made
                           by this client.  Setting this allows Lendsmart's internal
                           monitoring applications to track the usage of your
                           application.  Setting this is not necessary, but some
                           applications may desire this behavior.
        :type user_agent: str
        """
        self.base_url = base_url
        self._add_user_agent = user_agent
        self.service_account = service_account
        self.session = requests.Session()

        #: Access information related to the Prediction service - see
        #: :any:`PredictionGroup` for more information
        self.prediction = PredictionGroup(self)
        self.document = Documents(self)
        self.signature = AccountSignGroup(self)

    @property
    def _user_agent(self):
        return '{}python-lendsmart_api/{} {}'.format(
            '{} '.format(self._add_user_agent) if self._add_user_agent else '',
            package_version,
            requests.utils.default_user_agent()
        )

    def load(self, target_type, target_id, target_parent_id=None):
        """
        Constructs and immediately loads the object, circumventing the
        lazy-loading scheme by immediately making an API request.  Does not
        load related objects.

        For example, if you wanted to load an :any:`Instance` object with ID 123,
        you could do this::

           loaded_lendsmart = client.load(Instance, 123)

        Similarly, if you instead wanted to load a :any:`NodeBalancerConfig`,
        you could do so like this::

           loaded_nodebalancer_config = client.load(NodeBalancerConfig, 456, 432)

        :param target_type: The type of object to create.
        :type target_type: type
        :param target_id: The ID of the object to create.
        :type target_id: int or str
        :param target_parent_id: The parent ID of the object to create, if
                                 applicable.
        :type target_parent_id: int, str, or None

        :returns: The resulting object, fully loaded.
        :rtype: target_type
        :raise ApiError: if the requested object could not be loaded.
        """
        result = target_type.make_instance(
            target_id, self, parent_id=target_parent_id)
        result._api_get()

        return result

    def _api_call(self, endpoint, model=None, method=None, data=None, filters=None):
        """
        Makes a call to the lendsmart api.  Data should only be given if the method is
        POST or PUT, and should be a dictionary
        """
        if not self.service_account:
            raise RuntimeError("You do not have an API service account!")

        if not method:
            raise ValueError("Method is required for API calls!")

        if model:
            endpoint = endpoint.format(**vars(model))
        url = '{}{}'.format(self.base_url, endpoint)
        headers = {
            'Authorization': "Bearer {}".format(self.service_account.bearer_token().decode("utf-8")),
            'Content-Type': 'application/json',
            'User-Agent': self._user_agent,
            'X-AUTH-LENDSMART-SERVICE-ACCOUNT-NAME': self.service_account.CONST_SERVICE_ACCOUNT_NAME,
        }

        if filters:
            headers['X-Filter'] = json.dumps(filters)

        body = None
        if data is not None:
            body = json.dumps(data)

        response = method(url, headers=headers, data=body)
        warning = response.headers.get('Warning', None)
        if warning:
            logger.warning('Received warning from server: {}'.format(warning))
        
        if 399 < response.status_code < 600:
            j = None
            error_msg = '{}: '.format(response.status_code)
            try:
                j = response.json()
                if 'message' in j.keys():
                    error_msg += '{}; {} '.format(j['reason'], j['message'])

            except:
                pass
            raise ApiError(error_msg, status=response.status_code, json=j)

        if response.status_code != 204: 
            j = response.json()
        else:
            j = None  # handle no response body

        return j

    def _get_objects(self, endpoint, cls, model=None, parent_id=None, filters=None):
        response_json = self.get(endpoint, model=model, filters=filters)

        if not "data" in response_json:
            raise UnexpectedResponseError(
                "Problem with response!", json=response_json)

        if 'pages' in response_json:
            formatted_endpoint = endpoint
            if model:
                formatted_endpoint = formatted_endpoint.format(**vars(model))
            return PaginatedList.make_paginated_list(response_json, self, cls,
                                                     parent_id=parent_id, page_url=formatted_endpoint[1:],
                                                     filters=filters)
        return PaginatedList.make_list(response_json["data"], self, cls,
                                       parent_id=parent_id)

    def get(self, *args, **kwargs):
        return self._api_call(*args, method=self.session.get, **kwargs)

    def post(self, *args, **kwargs):
        return self._api_call(*args, method=self.session.post, **kwargs)

    def put(self, *args, **kwargs):
        return self._api_call(*args, method=self.session.put, **kwargs)

    def delete(self, *args, **kwargs):
        return self._api_call(*args, method=self.session.delete, **kwargs)

    def documents(self, *filters):
        """
        Retrieves a list of available Documents
        Document available to the acting user.

        :returns: A list of available Documents.
        :rtype: PaginatedList of Document
        """
        return self._get_and_filter(Document, *filters)

    def document_create(self, disk, label=None, description=None):
        """
        Creates a new Document

        :returns: The new Document.
        :rtype: Document
        """

        if label is not None:
            params = {
                "object_meta": {
                    "name": label["name"],
                    "account": label["account"]
                },
                "document_name": label["document_name"],
                "location": label["location"],
                "represents_schema": label["represents_schema"],
                "status": {
                    "phase": "Pending",
                    "message": "",
                    "reason": "",
                    "conditions": []
                }
            }

        if description is not None:
            params["description"] = description

        print("Params:", params)
        result = self.post('/documents', data=params)

        if not 'id' in result:
            raise UnexpectedResponseError('Unexpected response when creating an '
                                          'Document {}'.format(disk))

        return Document(self, result['id'], result)
