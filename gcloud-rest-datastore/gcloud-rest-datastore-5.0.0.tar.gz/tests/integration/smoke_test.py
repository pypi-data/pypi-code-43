from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import str
from builtins import range
from future import standard_library
standard_library.install_aliases()
import uuid

import pytest
from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint: disable=no-name-in-module
from gcloud.rest.datastore import Datastore
from gcloud.rest.datastore import Filter
from gcloud.rest.datastore import GQLQuery
from gcloud.rest.datastore import Key
from gcloud.rest.datastore import Operation
from gcloud.rest.datastore import PathElement
from gcloud.rest.datastore import Projection
from gcloud.rest.datastore import PropertyFilter
from gcloud.rest.datastore import PropertyFilterOperator
from gcloud.rest.datastore import Query
from gcloud.rest.datastore import Value
from gcloud.rest.storage import Storage  # pylint: disable=no-name-in-module

# Selectively load libraries based on the package
if BUILD_GCLOUD_REST:
    from requests import Session
    from time import sleep
else:
    from aiohttp import ClientSession as Session
    from asyncio import sleep


#@pytest.mark.asyncio  # type: ignore
def test_item_lifecycle(creds     , kind     , project     )        :
    key = Key(project, [PathElement(kind)])

    with Session() as s:
        ds = Datastore(project=project, service_file=creds, session=s)

        allocatedKeys = ds.allocateIds([key], session=s)
        assert len(allocatedKeys) == 1
        key.path[-1].id = allocatedKeys[0].path[-1].id
        assert key == allocatedKeys[0]

        ds.reserveIds(allocatedKeys, session=s)

        props_insert = {'is_this_bad_data': True}
        ds.insert(allocatedKeys[0], props_insert, session=s)
        actual = ds.lookup([allocatedKeys[0]], session=s)
        assert actual['found'][0].entity.properties == props_insert

        props_update = {'animal': 'aardvark', 'overwrote_bad_data': True}
        ds.update(allocatedKeys[0], props_update, session=s)
        actual = ds.lookup([allocatedKeys[0]], session=s)
        assert actual['found'][0].entity.properties == props_update

        props_upsert = {'meaning_of_life': 42}
        ds.upsert(allocatedKeys[0], props_upsert, session=s)
        actual = ds.lookup([allocatedKeys[0]], session=s)
        assert actual['found'][0].entity.properties == props_upsert

        ds.delete(allocatedKeys[0], session=s)
        actual = ds.lookup([allocatedKeys[0]], session=s)
        assert len(actual['missing']) == 1


#@pytest.mark.asyncio  # type: ignore
def test_transaction(creds     , kind     , project     )        :
    key = Key(project, [PathElement(kind, name='test_record_{}'.format((uuid.uuid4())))])

    with Session() as s:
        ds = Datastore(project=project, service_file=creds, session=s)

        transaction = ds.beginTransaction(session=s)
        actual = ds.lookup([key], transaction=transaction, session=s)
        assert len(actual['missing']) == 1

        mutations = [
            ds.make_mutation(Operation.INSERT, key,
                             properties={'animal': 'three-toed sloth'}),
            ds.make_mutation(Operation.UPDATE, key,
                             properties={'animal': 'aardvark'}),
        ]
        ds.commit(mutations, transaction=transaction, session=s)

        actual = ds.lookup([key], session=s)
        assert actual['found'][0].entity.properties == {'animal': 'aardvark'}


#@pytest.mark.asyncio  # type: ignore
def test_rollback(creds     , project     )        :
    with Session() as s:
        ds = Datastore(project=project, service_file=creds, session=s)

        transaction = ds.beginTransaction(session=s)
        ds.rollback(transaction, session=s)

#@pytest.mark.asyncio  # type: ignore
def test_query_with_key_projection(creds     , kind     ,
                                         project     )        :
    with Session() as s:
        ds = Datastore(project=project, service_file=creds, session=s)
        # setup test data
        ds.insert(Key(project, [PathElement(kind)]), {'value': 30}, s)
        property_filter = PropertyFilter(
            prop='value', operator=PropertyFilterOperator.EQUAL,
            value=Value(30))
        projection = [Projection.from_repr({'property': {'name': '__key__'}})]

        query = Query(kind=kind, query_filter=Filter(property_filter), limit=1,
                      projection=projection)
        result = ds.runQuery(query, session=s)
        assert result.entity_results[0].entity.properties == {}
        assert result.entity_result_type.value == 'KEY_ONLY'
        # clean up test data
        ds.delete(result.entity_results[0].entity.key, s)

#@pytest.mark.asyncio  # type: ignore
def test_query_with_value_projection(creds     , kind     ,
                                           project     )        :
    with Session() as s:
        ds = Datastore(project=project, service_file=creds, session=s)
        # setup test data
        ds.insert(Key(project, [PathElement(kind)]), {'value': 30}, s)
        projection = [Projection.from_repr({'property': {'name': 'value'}})]

        query = Query(kind=kind, limit=1,
                      projection=projection)
        result = ds.runQuery(query, session=s)
        assert result.entity_result_type.value == 'PROJECTION'
        # clean up test data
        ds.delete(result.entity_results[0].entity.key, s)

#@pytest.mark.asyncio  # type: ignore
def test_query_with_distinct_on(creds     , kind     ,
                                      project     )        :
    keys1 = [Key(project, [PathElement(kind)]) for i in range(3)]
    keys2 = [Key(project, [PathElement(kind)]) for i in range(3)]
    with Session() as s:
        ds = Datastore(project=project, service_file=creds, session=s)

        # setup test data
        allocatedKeys1 = ds.allocateIds(keys1, session=s)
        allocatedKeys2 = ds.allocateIds(keys2, session=s)
        for key1 in allocatedKeys1:
            ds.insert(key1, {'dist_value': 11}, s)
        for key2 in allocatedKeys2:
            ds.insert(key2, {'dist_value': 22}, s)
        query = Query(kind=kind, limit=10, distinct_on=['dist_value'])
        result = ds.runQuery(query, session=s)
        assert len(result.entity_results) == 2
        # clean up test data
        for key1 in allocatedKeys1:
            ds.delete(key1, s)
        for key2 in allocatedKeys2:
            ds.delete(key2, s)


#@pytest.mark.asyncio  # type: ignore
@pytest.mark.xfail(strict=False)  # type: ignore
def test_query(creds     , kind     , project     )        :
    with Session() as s:
        ds = Datastore(project=project, service_file=creds, session=s)

        property_filter = PropertyFilter(
            prop='value', operator=PropertyFilterOperator.EQUAL,
            value=Value(42))
        query = Query(kind=kind, query_filter=Filter(property_filter))

        before = ds.runQuery(query, session=s)
        num_results = len(before.entity_results)

        transaction = ds.beginTransaction(session=s)
        mutations = [
            ds.make_mutation(Operation.INSERT,
                             Key(project, [PathElement(kind)]),
                             properties={'value': 42}),
            ds.make_mutation(Operation.INSERT,
                             Key(project, [PathElement(kind)]),
                             properties={'value': 42}),
        ]
        ds.commit(mutations, transaction=transaction, session=s)

        after = ds.runQuery(query, session=s)
        assert len(after.entity_results) == num_results + 2


#@pytest.mark.asyncio  # type: ignore
@pytest.mark.xfail(strict=False)  # type: ignore
def test_gql_query(creds     , kind     , project     )        :
    with Session() as s:
        ds = Datastore(project=project, service_file=creds, session=s)

        query = GQLQuery('SELECT * FROM {} WHERE value = @value'.format((kind)),
                         named_bindings={'value': 42})

        before = ds.runQuery(query, session=s)
        num_results = len(before.entity_results)

        transaction = ds.beginTransaction(session=s)
        mutations = [
            ds.make_mutation(Operation.INSERT,
                             Key(project, [PathElement(kind)]),
                             properties={'value': 42}),
            ds.make_mutation(Operation.INSERT,
                             Key(project, [PathElement(kind)]),
                             properties={'value': 42}),
            ds.make_mutation(Operation.INSERT,
                             Key(project, [PathElement(kind)]),
                             properties={'value': 42}),
        ]
        ds.commit(mutations, transaction=transaction, session=s)

        after = ds.runQuery(query, session=s)
        assert len(after.entity_results) == num_results + 3


@pytest.mark.skip
#@pytest.mark.asyncio  # type: ignore
def test_datastore_export(creds     , project     ,
                                export_bucket_name     ):
    kind = 'PublicTestDatastoreExportModel'

    rand_uuid = str(uuid.uuid4())

    with Session() as s:
        ds = Datastore(project=project, service_file=creds, session=s)

        ds.insert(Key(project, [PathElement(kind)]),
                        properties={'rand_str': rand_uuid})

        operation = ds.export(export_bucket_name, kinds=[kind])

        count = 0
        while (count < 10 and operation and
               operation.metadata['common']['state'] == 'PROCESSING'):
            sleep(10)
            operation = ds.get_datastore_operation(operation.name)
            count += 1

        assert operation.metadata['common']['state'] == 'SUCCESSFUL'

        prefix_len = len('gs://{}/'.format((export_bucket_name)))
        export_path = operation.metadata['outputUrlPrefix'][prefix_len:]

        storage = Storage(service_file=creds, session=s)
        files = storage.list_objects(export_bucket_name,
                                           params={'prefix': export_path})
        for file in files['items']:
            storage.delete(export_bucket_name, file['name'])
