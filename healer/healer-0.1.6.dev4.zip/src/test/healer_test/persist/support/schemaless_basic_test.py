import os
import tempfile

from healer.persist.support.schemaless import *


def xtest_table_digest():
    print()

    datafile = tempfile.mktemp(prefix="nosql-digest-", suffix=".db")
    database = NoSqlDatabase(datafile)
    server_store = database.store('server_store')
    server_store.issue_create()

    user_1 = server_store.ensure_record(
        record="091a267e-068e-400b-b57e-7d4cc3d4f54f",
        user={
            'username': 'coleifer1',
            'location': {'city': 'Lawrence', 'state': 'KS'},
        },
        social=[
            {'name': 'github', 'username': 'coleifer'},
            {'name': 'twitter', 'username': 'coleifer'},
        ],
        antisocial=[
            {'name': 'github', 'username': 'coleifer'},
            {'name': 'twitter', 'username': 'coleifer'},
        ])

    content_digest = server_store.content_digest()
    print(f"content_digest={content_digest}")

    journal_digest = server_store.journal_digest()
    print(f"journal_digest={journal_digest}")

    server_store.issue_delete()
    database.close()
    os.remove(datafile)


def test_basic_nosql():
    print()

    datafile = tempfile.mktemp(prefix="nosql-basic-", suffix=".db")
    database = NoSqlDatabase(datafile)
    server_store = database.store('server_store')
    server_store.issue_create()

    reactor_event_map = dict()

    class Replicator(NoSqlReplicator):

        def react_apply_event(self, event:NoSqlEvent) -> None:
            print(f"APPLY: {event}")

        def react_local_event(self, event:NoSqlEvent) -> None:
            print(f"LOCAL: {event}")
            reactor_event_map[event.token] = event

    replicator = Replicator()

    server_store.bind_reactor(replicator)

    index_username = server_store.ensure_index('user', '$.username')
    index_location_state = server_store.ensure_index('user', '$.location.state')

    user_1 = server_store.ensure_record(
        record="091a267e-068e-400b-b57e-7d4cc3d4f54f",
        user={
            'username': 'coleifer1',
            'location': {'city': 'Lawrence', 'state': 'KS'},
        },
        social=[
            {'name': 'github', 'username': 'coleifer'},
            {'name': 'twitter', 'username': 'coleifer'},
        ],
        antisocial=[
            {'name': 'github', 'username': 'coleifer'},
            {'name': 'twitter', 'username': 'coleifer'},
        ])
#     print(f"user_1: {user_1}")
#     print(user_1.to_event('create', 'user'))

    user_2 = server_store.ensure_record(
        user={
            'username': 'coleifer2',
            'location': {'city': 'Lawrence', 'state': 'KS'},
        },
        social=[
            {'name': 'twitter', 'username': 'coleifer'},
        ])
#     print(f"user_2: {user_2}")
#     print(user_2.to_event('create', 'user'))

    print(index_username.entry_list())

#     location_query_1 = index_location_state.query('KS')
#     print(f"location_query_1={location_query_1}")
#     for record in location_query_1:
#         print(f"1 record={record}")
#         user = record['user']
#         print(f"2 user/username={user['username']}")
#         user['username'] = 'coleifer3'
#         record['user'] = user
# #         record.delete()
#         print(f"3 record={record}")

#     location_query_2 = index_location_state.query('KS')
#     print(f"location_query_2={location_query_2}")
#     for record in location_query_2:
#         print(f"4 record={record}")
#         user = record['user']
#         print(f"5 user/username={user['username']}")
#         user['username'] = 'coleifer4'
#         record['user'] = user
# #         record.delete()
#         print(f"6 record={record}")

#     reactor_map = reactor_event_map.copy()

#     for key in reactor_map.keys():
#         print(key)
#         event = reactor_map[key]
#         replicator.apply_event(event)

#     replicator.unbind()
#     server_store.issue_delete()
#     database.close()
#     os.remove(datafile)
