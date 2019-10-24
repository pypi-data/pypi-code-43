from copy import deepcopy
from time import sleep
from uuid import uuid4, UUID

from bson import Binary, binary

from cocktail_apikit import DictMongoQueryBuilder, MongoDBManager
from cocktail_apikit.utils_kit import build_mongodb_uuid, convert_py_uuid_to_mongodb_uuid


def populate_with_pets(db_client):
    db_client.create({'_id': build_mongodb_uuid(uuid4()), 'name': 'cat red'})
    db_client.create({'_id': build_mongodb_uuid(uuid4()), 'name': 'dog blue'})
    db_client.create({'_id': build_mongodb_uuid(uuid4()), 'name': 'duck yellow'})


def test_dict_mongo_query_builder_or_conditional(demo_schema):
    query_dict = dict()
    query_dict['or'] = [
        {"name": 'person name'},
        {"documents.number": '552244554789'}
    ]

    builder = DictMongoQueryBuilder(query_data=query_dict, schema=demo_schema)
    mongo_query = builder.to_mongo_query()
    mongo_query_dict = mongo_query.to_dict()

    assert mongo_query_dict['or'] == [{'name': 'person name'}, {'documents.number': '552244554789'}]


def test_dict_mongo_query_builder(demo_schema):
    id_value = str(uuid4())
    query_dict = {'name__eq': 'demo', 'id__ne': id_value}

    builder = DictMongoQueryBuilder(query_data=query_dict, schema=demo_schema)

    mongo_query = builder.to_mongo_query()

    print(mongo_query.to_dict())
    mongo_query_dict = mongo_query.to_dict()

    assert mongo_query_dict['name'] == {'$eq': 'demo'}
    assert mongo_query_dict['_id'] == {'$ne': Binary(UUID(id_value).bytes, binary.STANDARD)}

    for key in ['sort', 'projection', 'page', 'limit', 'skip']:
        assert key in mongo_query_dict


def test__mongo_db_manager__caching_connection_ok(mongo_uri):
    config1 = {'MONGODB_URI': mongo_uri, 'DB_NAME': 'testDB', 'COLLECTION_NAME': 'demos'}
    config2 = {'MONGODB_URI': mongo_uri, 'DB_NAME': 'testDB', 'COLLECTION_NAME': 'demos2'}
    config3 = {'MONGODB_URI': mongo_uri, 'DB_NAME': 'testDB', 'COLLECTION_NAME': 'demos3'}
    db1 = MongoDBManager(config1)
    db2 = MongoDBManager(config2)
    db3 = MongoDBManager(config3)

    assert db1.CLIENTS == db2.CLIENTS == db3.CLIENTS
    assert len(db1.CLIENTS) == len(db2.CLIENTS) == len(db3.CLIENTS) == 1
    assert db1.collection.name == 'demos'
    assert db2.collection.name == 'demos2'
    assert db3.collection.name == 'demos3'


def test_mongo_query_object_to_dict_no_in_place_update(demo_schema):
    id_value = str(uuid4())
    query_dict = {'name__eq': 'demo', 'id__ne': id_value}

    builder = DictMongoQueryBuilder(query_data=query_dict, schema=demo_schema)

    mongo_query = builder.to_mongo_query()
    query_condition = deepcopy(mongo_query.condition)
    mongo_query.to_dict()
    assert query_condition == mongo_query.condition


def test_filter_with_aggregate_find(db_client, demo_schema):
    populate_with_pets(db_client)
    query_dict = {'name': 'dog blue'}
    builder = DictMongoQueryBuilder(query_data=query_dict, schema=demo_schema)
    mongo_query = builder.to_mongo_query()
    results, count = db_client.filter_with_aggregate(mongo_query)
    pet_names = map(lambda pet: pet['name'], results)
    assert 'dog blue' in pet_names
    assert 'cat red' not in pet_names


def test_filter_with_aggregate_sort(db_client, demo_schema):
    populate_with_pets(db_client)
    query_dict = {'sort': ['-name']}
    builder = DictMongoQueryBuilder(query_data=query_dict, schema=demo_schema)
    mongo_query = builder.to_mongo_query()
    results, count = db_client.filter_with_aggregate(mongo_query)
    pet_names = list(map(lambda pet: pet['name'], list(results)))
    assert ['duck yellow', 'dog blue', 'cat red'] == pet_names


def test_filter_with_aggregate_limit(db_client, demo_schema):
    populate_with_pets(db_client)
    query_dict = {'limit': 1}
    builder = DictMongoQueryBuilder(query_data=query_dict, schema=demo_schema)
    mongo_query = builder.to_mongo_query()
    results, count = db_client.filter_with_aggregate(mongo_query)
    assert len(list(results)) == 1


def test_filter_with_aggregate_pagination(db_client, demo_schema):
    populate_with_pets(db_client)
    query_dict = {'page': 3, 'limit': 1}
    builder = DictMongoQueryBuilder(query_data=query_dict, schema=demo_schema)
    mongo_query = builder.to_mongo_query()
    results, count = db_client.filter_with_aggregate(mongo_query)
    assert list(results)[0]['name'] == 'duck yellow'


def test_filter_with_aggregate_text_search(db_client, demo_schema):
    populate_with_pets(db_client)
    db_client.collection.create_index([('name', 'text')])
    query_dict = {}
    builder = DictMongoQueryBuilder(query_data=query_dict, schema=demo_schema)
    mongo_query = builder.to_mongo_query()
    results, count = db_client.filter_with_aggregate(mongo_query, text_search='cat')
    result_list = list(results)
    assert result_list[0]['name'] == 'cat red'
    assert len(result_list) == 1


def test_filter_with_aggregate_relations(db_client, demo_schema):
    populate_with_pets(db_client)
    cat = list(db_client.find())[0]

    db_client.db.get_collection('pet_sounds').insert_one({'_id': convert_py_uuid_to_mongodb_uuid(cat['_id']),
                                                          'sound': 'Meow', '_enabled': True})
    query_dict = {
        '_id': cat['_id'],
        'lookup': {
            'from': 'pet_sounds',
            'localField': '_id',
            'foreignField': '_id',
            'as': 'sounds',
        },
        'unwind': '$sounds'
    }

    builder = DictMongoQueryBuilder(query_data=query_dict, schema=demo_schema)
    mongo_query = builder.to_mongo_query()
    results, count = db_client.filter_with_aggregate(mongo_query)
    list_results = list(results)
    assert list_results[0]['sounds']['sound'] == 'Meow'


def test_build_range_filter_with_schema_fields(demo_schema):
    query = {'name__in': 'hello,world',
             'id__in': '70dafa5e-d574-4b95-840e-1d14be8da7ad,212a1e2d-f674-44f5-9d8d-b2873647bf10'}
    builder = DictMongoQueryBuilder(query_data=query, schema=demo_schema)
    mongo_query = builder.to_mongo_query().to_dict()
    assert 'name' in mongo_query
    assert isinstance(mongo_query['name']['$in'], list)
    assert all([isinstance(o, str) for o in mongo_query['name']['$in']])

    assert '_id' in mongo_query
    assert isinstance(mongo_query['_id']['$in'], list)
    assert all([isinstance(o, Binary) and o.subtype == 4 for o in mongo_query['_id']['$in']])
