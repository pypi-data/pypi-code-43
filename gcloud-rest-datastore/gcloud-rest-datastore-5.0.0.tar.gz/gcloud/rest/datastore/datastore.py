from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import str
from future import standard_library
standard_library.install_aliases()
from builtins import object
import io
import logging
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from gcloud.rest.auth import SyncSession  # pylint: disable=no-name-in-module
from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint: disable=no-name-in-module
from gcloud.rest.auth import Token  # pylint: disable=no-name-in-module
from gcloud.rest.datastore.constants import Consistency
from gcloud.rest.datastore.constants import Mode
from gcloud.rest.datastore.constants import Operation
from gcloud.rest.datastore.datastore_operation import DatastoreOperation
from gcloud.rest.datastore.entity import EntityResult
from gcloud.rest.datastore.key import Key
from gcloud.rest.datastore.query import BaseQuery
from gcloud.rest.datastore.query import QueryResultBatch
from gcloud.rest.datastore.value import Value
try:
    import ujson as json
except ImportError:
    import json  # type: ignore

# Selectively load libraries based on the package
if BUILD_GCLOUD_REST:
    from requests import Session
else:
    from aiohttp import ClientSession as Session

try:
    API_ROOT = 'http://{}/v1'.format((os.environ["DATASTORE_EMULATOR_HOST"]))
    IS_DEV = True
except KeyError:
    API_ROOT = 'https://datastore.googleapis.com/v1'
    IS_DEV = False

SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/datastore',
]

log = logging.getLogger(__name__)


class Datastore(object):
    datastore_operation_kind = DatastoreOperation
    entity_result_kind = EntityResult
    key_kind = Key
    query_result_batch_kind = QueryResultBatch
    value_kind = Value

    def __init__(self, project                = None,
                 service_file                                  = None,
                 namespace      = '', session                    = None,
                 token                  = None)        :
        self.namespace = namespace
        self.session = SyncSession(session)

        if IS_DEV:
            self._project = os.environ.get('DATASTORE_PROJECT_ID', 'dev')
            # Tokens are not needed when using dev emulator
            self.token = None
        else:
            self._project = project
            self.token = token or Token(service_file=service_file,
                                        session=self.session.session,
                                        scopes=SCOPES)

    def project(self)       :
        if self._project:
            return self._project

        self._project = self.token.get_project()
        if self._project:
            return self._project

        raise Exception('could not determine project, please set it manually')

    @staticmethod
    def _make_commit_body(mutations                      ,
                          transaction                = None,
                          mode       = Mode.TRANSACTIONAL)                  :
        if not mutations:
            raise Exception('at least one mutation record is required')

        if transaction is None and mode != Mode.NON_TRANSACTIONAL:
            raise Exception('a transaction ID must be provided when mode is '
                            'transactional')

        data = {
            'mode': mode.value,
            'mutations': mutations,
        }
        if transaction is not None:
            data['transaction'] = transaction
        return data

    def headers(self)                  :
        if IS_DEV:
            return {}

        token = self.token.get()
        return {
            'Authorization': 'Bearer {}'.format((token)),
        }

    # TODO: support mutations w version specifiers, return new version (commit)
    @classmethod
    def make_mutation(cls, operation           , key     ,
                      properties                 = None)                  :
        if operation == Operation.DELETE:
            return {operation.value: key.to_repr()}

        return {
            operation.value: {
                'key': key.to_repr(),
                'properties': {k: cls.value_kind(v).to_repr()
                               for k, v in properties.items()},
            }
        }

    # https://cloud.google.com/datastore/docs/reference/data/rest/v1/projects/allocateIds
    def allocateIds(self, keys           ,
                          session                    = None,
                          timeout      = 10)             :
        project = self.project()
        url = '{}/projects/{}:allocateIds'.format((API_ROOT), (project))

        payload = json.dumps({
            'keys': [k.to_repr() for k in keys],
        }).encode('utf-8')

        headers = self.headers()
        headers.update({
            'Content-Length': str(len(payload)),
            'Content-Type': 'application/json',
        })

        s = SyncSession(session) if session else self.session
        resp = s.post(url, data=payload, headers=headers, timeout=timeout)
        data = resp.json()

        return [self.key_kind.from_repr(k) for k in data['keys']]

    # https://cloud.google.com/datastore/docs/reference/data/rest/v1/projects/beginTransaction
    # TODO: support readwrite vs readonly transaction types
    def beginTransaction(self, session                    = None,
                               timeout      = 10)       :
        project = self.project()
        url = '{}/projects/{}:beginTransaction'.format((API_ROOT), (project))
        headers = self.headers()
        headers.update({
            'Content-Length': '0',
            'Content-Type': 'application/json',
        })

        s = SyncSession(session) if session else self.session
        resp = s.post(url, headers=headers, timeout=timeout)
        data = resp.json()

        transaction      = data['transaction']
        return transaction

    # TODO: return mutation results
    # https://cloud.google.com/datastore/docs/reference/data/rest/v1/projects/commit
    def commit(self, mutations                      ,
                     transaction                = None,
                     mode       = Mode.TRANSACTIONAL,
                     session                    = None,
                     timeout      = 10)        :
        project = self.project()
        url = '{}/projects/{}:commit'.format((API_ROOT), (project))

        body = self._make_commit_body(mutations, transaction=transaction,
                                      mode=mode)
        payload = json.dumps(body).encode('utf-8')

        headers = self.headers()
        headers.update({
            'Content-Length': str(len(payload)),
            'Content-Type': 'application/json',
        })

        s = SyncSession(session) if session else self.session
        s.post(url, data=payload, headers=headers, timeout=timeout)

    # https://cloud.google.com/datastore/docs/reference/admin/rest/v1/projects/export
    def export(self, output_bucket_prefix     ,
                     kinds                      = None,
                     namespaces                      = None,
                     labels                           = None,
                     session                    = None,
                     timeout      = 10)                      :
        project = self.project()
        url = '{}/projects/{}:export'.format((API_ROOT), (project))

        payload = json.dumps({
            'entityFilter': {
                'kinds': kinds or [],
                'namespaceIds': namespaces or [],
            },
            'labels': labels or {},
            'outputUrlPrefix': 'gs://{}'.format((output_bucket_prefix)),
        }).encode('utf-8')

        headers = self.headers()
        headers.update({
            'Content-Length': str(len(payload)),
            'Content-Type': 'application/json',
        })

        s = SyncSession(session) if session else self.session
        resp = s.post(url, data=payload, headers=headers,
                            timeout=timeout)
        data       = resp.json()

        return self.datastore_operation_kind.from_repr(data)

    # https://cloud.google.com/datastore/docs/reference/data/rest/v1/projects.operations/get
    def get_datastore_operation(self, name     ,
                                      session                    = None,
                                      timeout      = 10)                      :
        url = '{}/{}'.format((API_ROOT), (name))

        headers = self.headers()
        headers.update({
            'Content-Type': 'application/json',
        })

        s = SyncSession(session) if session else self.session
        resp = s.get(url, headers=headers, timeout=timeout)
        data       = resp.json()

        return self.datastore_operation_kind.from_repr(data)

    # https://cloud.google.com/datastore/docs/reference/data/rest/v1/projects/lookup
    def lookup(self, keys           , transaction      = None,
                     consistency              = Consistency.STRONG,
                     session                    = None,
                     timeout      = 10)                                       :
        project = self.project()
        url = '{}/projects/{}:lookup'.format((API_ROOT), (project))

        if transaction:
            options = {'transaction': transaction}
        else:
            options = {'readConsistency': consistency.value}
        payload = json.dumps({
            'keys': [k.to_repr() for k in keys],
            'readOptions': options,
        }).encode('utf-8')

        headers = self.headers()
        headers.update({
            'Content-Length': str(len(payload)),
            'Content-Type': 'application/json',
        })

        s = SyncSession(session) if session else self.session
        resp = s.post(url, data=payload, headers=headers, timeout=timeout)

        data       = resp.json()

        return {
            'found': [self.entity_result_kind.from_repr(e)
                      for e in data.get('found', [])],
            'missing': [self.entity_result_kind.from_repr(e)
                        for e in data.get('missing', [])],
            'deferred': [self.key_kind.from_repr(k)
                         for k in data.get('deferred', [])],
        }

    # https://cloud.google.com/datastore/docs/reference/data/rest/v1/projects/reserveIds
    def reserveIds(self, keys           , database_id      = '',
                         session                    = None,
                         timeout      = 10)        :
        project = self.project()
        url = '{}/projects/{}:reserveIds'.format((API_ROOT), (project))

        payload = json.dumps({
            'databaseId': database_id,
            'keys': [k.to_repr() for k in keys],
        }).encode('utf-8')

        headers = self.headers()
        headers.update({
            'Content-Length': str(len(payload)),
            'Content-Type': 'application/json',
        })

        s = SyncSession(session) if session else self.session
        s.post(url, data=payload, headers=headers, timeout=timeout)

    # https://cloud.google.com/datastore/docs/reference/data/rest/v1/projects/rollback
    def rollback(self, transaction     ,
                       session                    = None,
                       timeout      = 10)        :
        project = self.project()
        url = '{}/projects/{}:rollback'.format((API_ROOT), (project))

        payload = json.dumps({
            'transaction': transaction,
        }).encode('utf-8')

        headers = self.headers()
        headers.update({
            'Content-Length': str(len(payload)),
            'Content-Type': 'application/json',
        })

        s = SyncSession(session) if session else self.session
        s.post(url, data=payload, headers=headers, timeout=timeout)

    # https://cloud.google.com/datastore/docs/reference/data/rest/v1/projects/runQuery
    def runQuery(self, query           , transaction      = None,
                       consistency              = Consistency.EVENTUAL,
                       session                    = None,
                       timeout      = 10)                    :
        project = self.project()
        url = '{}/projects/{}:runQuery'.format((API_ROOT), (project))

        if transaction:
            options = {'transaction': transaction}
        else:
            options = {'readConsistency': consistency.value}
        payload = json.dumps({
            'partitionId': {
                'projectId': project,
                'namespaceId': self.namespace,
            },
            query.json_key:  query.to_repr(),
            'readOptions': options,
        }).encode('utf-8')

        headers = self.headers()
        headers.update({
            'Content-Length': str(len(payload)),
            'Content-Type': 'application/json',
        })

        s = SyncSession(session) if session else self.session
        resp = s.post(url, data=payload, headers=headers, timeout=timeout)

        data       = resp.json()
        return self.query_result_batch_kind.from_repr(data['batch'])

    def delete(self, key     ,
                     session                    = None)        :
        return self.operate(Operation.DELETE, key, session=session)

    def insert(self, key     , properties                ,
                     session                    = None)        :
        return self.operate(Operation.INSERT, key, properties,
                                  session=session)

    def update(self, key     , properties                ,
                     session                    = None)        :
        return self.operate(Operation.UPDATE, key, properties,
                                  session=session)

    def upsert(self, key     , properties                ,
                     session                    = None)        :
        return self.operate(Operation.UPSERT, key, properties,
                                  session=session)

    # TODO: accept Entity rather than key/properties?
    def operate(self, operation           , key     ,
                      properties                 = None,
                      session                    = None)        :
        transaction = self.beginTransaction(session=session)
        mutation = self.make_mutation(operation, key, properties=properties)
        self.commit([mutation], transaction=transaction, session=session)
