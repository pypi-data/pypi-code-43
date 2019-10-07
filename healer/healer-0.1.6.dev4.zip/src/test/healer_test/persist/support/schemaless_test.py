import os
import sys
import json
import tempfile
import operator
import unittest

from healer.persist.support.schemaless import *


class StoreTest(unittest.TestCase):

    def setUp(self):
        self.database = NoSqlDatabase(':memory:')
        self.store_number = 0

    def tearDown(self):
        self.database.close()

    def produce_store(self) -> NoSqlStore:
        self.store_number += 1
        store_name = f"store_{self.store_number}"
        store = self.database.store(store_name)
        store.issue_create()
        return store

    def test_storage(self):

        store = self.produce_store()

        charlie = store.ensure_record()
        self.assertIsNone(charlie.row_id)

        # First write will allocate an record.
        charlie['name'] = 'charlie'
        self.assertIsNotNone(charlie.row_id)

        # Write some more col_ids.
        charlie['eyes'] = 'brown'
        charlie['hair'] = 'dark brown'

        huey = store.ensure_record()
        huey['name'] = 'huey'
        huey['eyes'] = 'blue'
        huey['fur'] = 'white'

        # Test retrieving data.
        c_db = store[charlie.row_id]
        self.assertEqual(c_db['name'], 'charlie')
        self.assertEqual(c_db['eyes'], 'brown')
        self.assertEqual(c_db['hair'], 'dark brown')

        h_db = store[huey.row_id]
        self.assertEqual(h_db['name'], 'huey')
        self.assertEqual(h_db['eyes'], 'blue')
        self.assertEqual(h_db['fur'], 'white')

        # Non-existant col_ids return NULL.
        self.assertIsNone(c_db['fur'])
        self.assertIsNone(h_db['hair'])

        # Overwriting values will pick the newest first. Since values are
        # cached, though, we will need to re-load from the database.
        huey['fur'] = 'white and gray'
        self.assertEqual(huey['fur'], 'white and gray')
        self.assertEqual(h_db['fur'], 'white')  # Old value.

        h_db = store[huey.row_id]
        self.assertEqual(h_db['fur'], 'white and gray')

        del huey['fur']
        self.assertIsNone(huey['fur'])
        self.assertEqual(h_db['fur'], 'white and gray')  # Old value.

        h_db = store[huey.row_id]
        self.assertIsNone(h_db['fur'])

    def test_update(self):

        store = self.produce_store()

        store_model = store.content_model
        charlie = store.ensure_record()
        self.assertIsNone(charlie.row_id)
        self.assertEqual(store_model.select().count(), 0)

        # First write will allocate an record.
        charlie['name'] = 'charlie'
        self.assertIsNotNone(charlie.row_id)
        self.assertEqual(store_model.select().count(), 1)

        charlie['country'] = 'US'
        charlie['state'] = 'KS'
        self.assertEqual(store_model.select().count(), 3)

        # Every insert will allocate an entry.
        charlie['state'] = 'Kansas'
        self.assertEqual(store_model.select().count(), 3)

        bundle = (store_model
                 .select(store_model.bundle)
                 .where(store_model.col_id == 'state')
                 .order_by(store_model.stamp.desc())
                 .scalar())
        self.assertEqual(bundle, 'Kansas')

        for index in range(10):
            charlie['sequence'] = index

        self.assertEqual(store_model.select().count(), 4)

        bundle = (store_model
                 .select(store_model.bundle)
                 .where(store_model.col_id == 'sequence')
                 .order_by(store_model.stamp.desc())
                 .scalar())
        self.assertEqual(bundle, 9)

    def test_record_iterator(self):

        store = self.produce_store()

        for instance in range(1, 5):
            row_id = uuid.uuid4()
            for version in range(1, 5):
                bucket = {
                    'instance': instance,
                    'version' : version,
                    'k1': f'v1-{version}',
                    'k2': f'v2-{version}',
                }
                store.ensure_record(row_id=row_id, **bucket)

        record_list = [record for record in store.record_iterator()]

        self.assertEqual([record.bucket for record in record_list],
        [
            {'instance': 1, 'k1': 'v1-4', 'k2': 'v2-4', 'version': 4},
            {'instance': 2, 'k1': 'v1-4', 'k2': 'v2-4', 'version': 4},
            {'instance': 3, 'k1': 'v1-4', 'k2': 'v2-4', 'version': 4},
            {'instance': 4, 'k1': 'v1-4', 'k2': 'v2-4', 'version': 4},
        ])

    def test_record_get_set(self):

        store = self.produce_store()

        r1 = store.ensure_record()
        r1['k1-1'] = 'v1'
        r1['k2-1'] = 'v2'
        r1['k3-1'] = 'v3'

        r2 = store.ensure_record()
        r2['k1-2'] = 'x1'
        r2['k2-2'] = 'x2'
        r2['k3-2'] = 'x3'

        r1_db = store.get_record(r1.row_id, ('k1-1', 'k3-1'))
        self.assertEqual(r1_db.bucket, {
            'k1-1': 'v1',
            'k3-1': 'v3'})

        # Load other values.
        self.assertEqual(r1_db['k1-1'], 'v1')
        self.assertEqual(r1_db['k2-1'], 'v2')
        self.assertEqual(r1_db.bucket, {
            'k1-1': 'v1',
            'k2-1': 'v2',
            'k3-1': 'v3'})

        r2_db = store.get_record(r2.row_id, (
            'k1-2',
            'k3-2',
            'kX-x',  # Non-existant col_id should not be loaded.
            'k2-1',  # Column from `r1` should not be loaded.
        ))
        self.assertEqual(r2_db.bucket, {
            'k1-2': 'x1',
            'k3-2': 'x3'})

        # Test loading all col_ids.
        r1_db2 = store.get_record(r1.row_id)
        self.assertEqual(r1_db2.bucket, {
            'k1-1': 'v1',
            'k2-1': 'v2',
            'k3-1': 'v3'})

    def test_create_with_data(self):

        store = self.produce_store()

        r1 = store.ensure_record(k1_1='v1', k2_1='v2', k3_1='v3')
        r2 = store.ensure_record(k1_2='x1', k2_2='x2', k3_2='x3')

        self.assertEqual(r1.bucket, {
            'k1_1': 'v1',
            'k2_1': 'v2',
            'k3_1': 'v3'})

        self.assertEqual(r2.bucket, {
            'k1_2': 'x1',
            'k2_2': 'x2',
            'k3_2': 'x3'})

        # Getting data works as expected.
        self.assertEqual(r1['k1_1'], 'v1')

        r1_dup = store[r1.row_id]
        self.assertEqual(r1_dup['k1_1'], 'v1')
        self.assertEqual(r1_dup['k2_1'], 'v2')
        self.assertEqual(r1_dup['k3_1'], 'v3')

        # No values from row2.
        self.assertIsNone(r1_dup['k1_2'])

    def test_index_query(self):

        store = self.database.store('storage_two')
        store.issue_create()

        index_username = store.ensure_index('user', '$.user.username')
        index_pet_name = store.ensure_index('user', '$.user.pets[0].name')

        charlie = {
            'user': {
                'username': 'charlie',
                'active': True,
                'pets': [
                    {'name': 'huey', 'type': 'cat'},
                    {'name': 'mickey', 'type': 'dog'},
                ],
            },
        }

        nuggie = {
            'user': {
                'username': 'nuggie',
                'active': True,
                'pets': [
                    {'name': 'zaizee', 'type': 'cat'},
                    {'name': 'beanie', 'type': 'cat'},
                ],
            },
        }

        store.ensure_record(user=charlie, misc={'foo': 'bar'})
        store.ensure_record(user=nuggie, misc={'foo': 'baze'})

#         for record in username.query('charlie'):
#             print(record)
#         for record in username.query('nuggie'):
#             print(record)
#         return

#         for record in store.record_iterator():
#             print(f"record: {record}")

        rows = [row for row in index_username.query('charlie')]
        self.assertEqual(len(rows), 1)
        row = rows[0]

        self.assertEqual(row.bucket,
        {
            'user': charlie,
            'misc': {'foo': 'bar'},
        })

        rows = [row for row in index_pet_name.query('zaizee')]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.bucket,
        {
            'user': nuggie,
            'misc': {'foo': 'baze'},
        })

    def prepare_index(self):

        store = self.produce_store()

        idx_k1 = store.ensure_index('data', '$.k1')

        store.ensure_record(data={'k1': 'v1-1'}, misc=1337)
        store.ensure_record(data={'k1': 'v1-2', 'k2': 'x1-2'})
        store.ensure_record(data={'k1': 'v1-3'}, k1='v1-5', k2='v1-6')
        store.ensure_record(data={'k1': 'xx', 'k2': 'x1-xx'})
        store.ensure_record(data={'k2': 'v1-x'})
        store.ensure_record(data={'k1': 'v1-4', 'k2': 'v1-y'})

        return store, idx_k1

    def test_query_expressions(self):
        store, idx_k1 = self.prepare_index()
        idx_k2 = store.ensure_index('data', '$.k2')

        query = idx_k1.query('v1-1') | idx_k1.query('v1-3') | idx_k1.query('xx')
        self.assertCountEqual([row.bucket['data']['k1'] for row in query], [
            'v1-1',
            'v1-3',
            'xx'])

        query = (idx_k1.query('v1-1') | idx_k1.query('v1-3')) | idx_k2.query('x1-xx')
        self.assertCountEqual([row.bucket['data'] for row in query], [
            {'k1': 'v1-1'},
            {'k1': 'v1-3'},
            {'k1': 'xx', 'k2': 'x1-xx'},
        ])

#     def test_query_descriptor(self):
#
#         store, idx_k1 = self.prepare_index()
#
#         idx_k2 = store.ensure_index('data', '$.k2')
#
#         query = idx_k1.query((idx_k1.v == 'v1-1') | (idx_k1.v == 'v1-3'))
#         self.assertCountEqual([row.bucket for row in query], [
#             {'data': {'k1': 'v1-1'}, 'misc': 1337},
#             {'data': {'k1': 'v1-3'}, 'k1': 'v1-5', 'k2': 'v1-6'},
#         ])
#
#         query = idx_k1.query((idx_k1.v == 'v1-1') | (idx_k1.v == 'v1-3'), reverse=True)
#         self.assertCountEqual([row.bucket for row in query], [
#             {'data': {'k1': 'v1-3'}, 'k1': 'v1-5', 'k2': 'v1-6'},
#             {'data': {'k1': 'v1-1'}, 'misc': 1337},
#         ])
#
#         idx1_q = idx_k1.query((idx_k1.v == 'v1-1') | (idx_k1.v == 'v1-3'))
#         idx2_q = idx_k2.query(idx_k2.v == 'x1-xx')
#         self.assertCountEqual([row.bucket['data'] for row in -(idx1_q | idx2_q)], [
#             {'k1': 'xx', 'k2': 'x1-xx'},
#             {'k1': 'v1-3'},
#             {'k1': 'v1-1'},
#         ])

    def test_multi_index(self):

        store, idx_k1 = self.prepare_index()

        rows = [row for row in idx_k1.query('v1-%', operator.pow)]
        self.assertEqual([row.bucket['data']['k1'] for row in rows], [
            'v1-1',
            'v1-2',
            'v1-3',
            'v1-4'])
        # All col_ids are fetched.
        self.assertEqual([row.bucket for row in rows], [
            {'data': {'k1': 'v1-1'}, 'misc': 1337},
            {'data': {'k1': 'v1-2', 'k2': 'x1-2'}},
            {'data': {'k1': 'v1-3'}, 'k1': 'v1-5', 'k2': 'v1-6'},
            {'data': {'k1': 'v1-4', 'k2': 'v1-y'}},
        ])

        rows = [row for row in idx_k1.query('v1-x')]
        self.assertEqual(rows, [])

        rows = [row for row in idx_k1.query('v1-2', operator.gt)]
        self.assertEqual([row.bucket['data']['k1'] for row in rows], [
            'v1-3',
            'xx',
            'v1-4'])

#     def test_index_delete(self):
#         store, idx_k1 = self.prepare_index()
#
#         all_items = [item for item in idx_k1.all_items()]
#         self.assertEqual(all_items, [
#             {'row_id': 1, 'bundle': 'v1-1'},
#             {'row_id': 2, 'bundle': 'v1-2'},
#             {'row_id': 3, 'bundle': 'v1-3'},
#             {'row_id': 4, 'bundle': 'xx'},
#             {'row_id': 6, 'bundle': 'v1-4'},
#         ])
#
#         row = store[2]
#         row.delete()
#
#         del store[4]
#
#         all_items = [item for item in idx_k1.all_items()]
#         self.assertEqual(all_items, [
#             {'row_id': 1, 'bundle': 'v1-1'},
#             {'row_id': 3, 'bundle': 'v1-3'},
#             {'row_id': 6, 'bundle': 'v1-4'},
#         ])

#     def test_index_populate(self):
#         idx_k1 = self.prepare_index()
#         store = idx_k1.store
#
#         idx_k2 = NoSqlIndex('data', '$.k2')
#         store.add_index(idx_k2)
#
#         self.assertEqual([row for row in idx_k2.all_items()], [
#             {'row_id': 2, 'bundle': u'x1-2'},
#             {'row_id': 4, 'bundle': u'x1-xx'},
#             {'row_id': 5, 'bundle': u'v1-x'},
#             {'row_id': 6, 'bundle': u'v1-y'},
#         ])
#

    def test_z_event_reactor(self):

        event_list = []

        class Reactor(NoSqlReactor):

            def react_event(self, event:NoSqlEvent) -> None:
                event_list.append(event)

        reactor = Reactor()

        store, idx_k1 = self.prepare_index()

        store.bind_reactor(reactor)

        store.ensure_record(data={'k1': 'v1'})
        store.ensure_record(data={'k2': 'v2'})
        store.ensure_record(data={'k3': 'v3', 'x3': 'y3'})
        self.assertEqual(len(event_list), 3)

        data_list = [(event.col_id, event.bundle) for event in event_list]

        self.assertEqual(data_list, [
            ('data', '{"k1":"v1"}'),
            ('data', '{"k2":"v2"}'),
            ('data', '{"k3":"v3","x3":"y3"}'),
        ])

        # Multiple col_ids correspond to multiple events.
        store.ensure_record(col1='val1', col2='val2')
        self.assertEqual(len(event_list), 5)

        event1 = event_list[3]
        event2 = event_list[4]
        self.assertEqual((event1.col_id, event1.bundle), ('col1', '"val1"'))
        self.assertEqual((event2.col_id, event2.bundle), ('col2', '"val2"'))

        # After unbinding, no more events.
        reactor.unbind()
        store.ensure_record(data={'k4': 'v4'})
        self.assertEqual(len(event_list), 5)
