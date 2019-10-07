import os
import sys
import json
import tempfile
import operator
import unittest

from healer.persist.support.schemaless import *


class VerifyTest(unittest.TestCase):

    def setUp(self):
        self.database = NoSqlDatabase(':memory:')
        self.store = self.database.store('storage')
        self.store.issue_create()

    def tearDown(self):
        self.store.issue_delete()
        self.database.close()

    def test_storage(self):

        row_id = uuid.uuid4()
        for index in range(1, 5):
            bucket = {'key_1':{'sub_1':f'value_{index}'}}
            self.store.ensure_record(row_id=row_id, **bucket)
        for index in range(1, 5):
            bucket = {'key_2':{'sub_1':f'value_{index}'}}
            self.store.ensure_record(row_id=row_id, **bucket)

        row_id = uuid.uuid4()
        for index in range(1, 5):
            bucket = {'key_1':{'sub_1':f'value_{index}'}}
            self.store.ensure_record(row_id=row_id, **bucket)
        for index in range(1, 5):
            bucket = {'key_2':{'sub_1':f'value_{index}'}}
            self.store.ensure_record(row_id=row_id, **bucket)

        store_model = self.store.content_model

        print(f"count={store_model.select().count()}")

        query_store = (store_model
            .select(
                store_model.row_id,
                store_model.col_id,
                store_model.bundle,
                store_model.token,
                store_model.stamp,
            )
        )

        print(f"query_store")
        for entry in query_store.tuples():
            print(entry)

        index_key_1 = self.store.ensure_index('key_1', '$.sub_1')

        index_model = index_key_1.index_model

        query_index = (index_model
            .select(
                index_model.row_id,
                index_model.resource,
            )
        )

        print(f"query_index")
        for entry in query_index.tuples():
            print(entry)

    def xxx_test_iteration(self):

        read_model = self.store.content_model
        write_model = self.store.journal_model

        print(f"count={read_model.select().count()}")

        query_select = (read_model
            .select(
                read_model.row_id,
                read_model.col_id,
                read_model.bundle,
                read_model.token,
                read_model.stamp,
            )
        )

        query_insert = lambda row_id: (write_model
            .insert(
                row_id=row_id,
                col_id='hello',
                bundle='{"a"=1}',
                action='create',
            )
        )

        for index in range(1, 5):
            bucket = {'key_1':{'sub_1':f'value_{index}'}}
            self.store.ensure_record(**bucket)

        print(f"iteration")
        for entry in query_select.tuples():
            print(entry)
            query_insert(uuid.uuid4().hex).execute()

