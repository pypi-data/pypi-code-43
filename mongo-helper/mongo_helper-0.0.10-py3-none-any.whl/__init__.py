import settings_helper as sh
import dt_helper as dh
import input_helper as ih
from collections import OrderedDict
from contextlib import suppress
from pymongo import MongoClient
from mongo_helper.queries import *


get_setting = sh.settings_getter(__name__)
mongo_url = get_setting('mongo_url')
SCALE_DICT = {
    'bytes': 1,
    'KB': 1024,
    'MB': 1048576,
    'GB': 1073741824
}


class Mongo(object):
    def __init__(self, url=None, db='db'):
        """An instance that can execute MongoDB statements

        - url: connection url to a MongoDB
        - db: name of db to use for making queries
        """
        self._client = MongoClient(url)
        self._db = db

    def get_databases(self, system=False):
        """Return a list of database names

        - system: if True, include the system dbs 'admin', 'config', and 'local'
        """
        ignore = []
        if not system:
            ignore = ['admin', 'config', 'local']
        return [
            name
            for name in self._client.list_database_names()
            if name not in ignore
        ]

    def change_database(self, db):
        """Set a different db to use for making queries"""
        self._db = db

    def select_database(self, system=False):
        """Interactively select a db to use for making queries

        - system: if True, include the system dbs 'admin', 'config', and 'local'
          in menu of dbs
        """
        selected = ih.make_selections(
            self.get_databases(system=system),
            prompt='Select database',
            one=True
        )
        if selected:
            self._db = selected

    def get_collections(self, db=None):
        """Return a list of collection names

        - db: if None, use current value in self._db
        """
        db = self._db if db is None else db
        return self._client[db].list_collection_names()

    def get_all_collections_for_all_databases(self, system=False):
        """Return a dict of database names and their collections

        - system: if True, include the system dbs 'admin', 'config', and 'local'
        """
        return {
            db: self.get_collections(db)
            for db in self.get_databases(system=system)
        }

    def db_stats(self, scale='bytes'):
        """Return a dict of info about the db

        - scale: one of bytes, KB, MB, GB
            - NOTE: avgObeSize is always in bytes no matter what the scale is

        See: https://docs.mongodb.com/manual/reference/command/dbStats/#output
        """
        try:
            scale_val = SCALE_DICT[scale]
        except KeyError:
            scale_val = 1
        return self._command('dbStats', scale=scale_val)

    def coll_stats(self, collection, ignore_fields='wiredTiger, indexDetails', scale='bytes'):
        """Return a dict of info about the collection

        - ignore_fields: string containing output fields to ignore, separated by
          any of , ; |
        - scale: one of bytes, KB, MB, GB
            - NOTE: avgObeSize is always in bytes no matter what the scale is

        See: https://docs.mongodb.com/manual/reference/command/collStats/#output
        """
        try:
            scale_val = SCALE_DICT[scale]
        except KeyError:
            scale_val = 1
        output = self._command('collStats', collection, scale=scale_val)
        if ignore_fields:
            output = ih.ignore_keys(output, ignore_fields)
        return output

    def server_status(self, ignore_fields='wiredTiger, tcmalloc, metrics, logicalSessionRecordCache'):
        """Return a dict of output from serverStatus db command

        - ignore_fields: string containing output fields to ignore, separated by
          any of , ; |

        See: https://docs.mongodb.com/manual/reference/command/serverStatus/#output
        """
        output = self._command('serverStatus')
        if ignore_fields:
            output = ih.ignore_keys(output, ignore_fields)
        return output

    def server_info(self, ignore_fields='buildEnvironment'):
        """Return a dict of output from self._client.server_info

        - ignore_fields: string containing output fields to ignore, separated by
          any of , ; |
        """
        output = self._client.server_info()
        if ignore_fields:
            output = ih.ignore_keys(output, ignore_fields)
        return output

    def _command(self, *args, **kwargs):
        """Run a db command and return the results"""
        db = self._db
        return self._client[db].command(*args, **kwargs)

    def _insert_one(self, collection, document):
        """Add a document to the collection and return inserted_id

        - document: a dict of info to be inserted
        """
        db = self._db
        result = self._client[db][collection].insert_one(document)
        return result.inserted_id

    def _insert_many(self, collection, list_of_dicts):
        """Add several documents to the collection and return inserted_ids"""
        db = self._db
        result = self._client[db][collection].insert_many(list_of_dicts)
        return result.inserted_ids

    def _update_one(self, collection, match, update, upsert=False):
        """Update one matching item from the collection and return num modified

        - match: a dict of the query matching document to update
        - update: dict of modifications to apply
        - upsert: if True, perform an insert if no documents match
        """
        db = self._db
        result = self._client[db][collection].update_one(match, update, upsert=upsert)
        return result.modified_count

    def _update_many(self, collection, match, update, upsert=False):
        """Update all matching items from the collection and return num modified

        - match: a dict of the query matching document to update
        - update: dict of modifications to apply
        - upsert: if True, perform an insert if no documents match
        """
        db = self._db
        result = self._client[db][collection].update_many(match, update, upsert=upsert)
        return result.modified_count

    def _delete_one(self, collection, match):
        """Delete one matching item from the collection and return num deleted

        - match: a dict of the query matching document to delete
        """
        db = self._db
        result = self._client[db][collection].delete_one(match)
        return result.deleted_count

    def _delete_many(self, collection, match):
        """Delete all matching items from the collection and return num deleted

        - match: a dict of the query matching documents to delete
        """
        db = self._db
        result = self._client[db][collection].delete_many(match)
        return result.deleted_count

    def _find(self, collection, *args, fields='', ignore_fields='', **kwargs):
        """Return a cursor

        - fields: string containing fields to return, separated by any of , ; |
        - ignore_fields: string containing fields to ignore, separated by any
          of , ; |
        - sort: list of (key, direction) pairs for sort order of results
        - limit: max number of results to return
        - skip: number of documents to omit from the start of result set
        - return_key: if True, only return the index keys in each document
        - max_time_ms: max number of milliseconds the find operation is allowed
          to run
        - hint: an index to use in the format passed to _create_index...
          [(field, direction)]
        - batch_size: limit number of documents returned in a single batch (> 1)
        - show_record_id: if True, add a '$recordId' field in each document
          with the storage engine's internal record identifier
        - no_cursor_timeout: if True, returned cursor will never timeout on the
          server (instead of being closed after 10 mins)
        - cursor_type: type of cursor to return:
            - pymongo.cursor.CursorType.NON_TAILABLE: standard cursor
            - pymongo.cursor.CursorType.TAILABLE: only for use with capped
              collections; cursor is not closed when last data received
                - if more data is received, iteration of cursor will continue
                  from last document received
            - pymongo.cursor.CursorType.TAILABLE_AWAIT: tailable cursor with
              await flag set
                - server will wait a few seconds after returning the full result
                  set so that it can capture and return additional data added
                  during the query
            - pymongo.cursor.CursorType.EXHAUST: stream batched results without
              waiting for client to request each batch
        """
        if fields and ignore_fields:
            raise Exception('Cannot specify both "fields" and "ignore_fields"')
        db = self._db
        fields = ih.get_list_from_arg_strings(fields)
        ignore_fields = ih.get_list_from_arg_strings(ignore_fields)
        if fields:
            kwargs['projection'] = {k: 1 for k in fields}
            if '_id' not in fields:
                kwargs['projection']['_id'] = 0
        if ignore_fields:
            kwargs['projection'] = {k: 0 for k in ignore_fields}
        return self._client[db][collection].find(*args, **kwargs)

    def _find_one(self, collection, *args, fields='', ignore_fields='', **kwargs):
        """Return an object

        - fields: string containing fields to return, separated by any of , ; |
        - ignore_fields: string containing fields to ignore, separated by any
          of , ; |

        Other kwargs are the same as those to _find
        """
        if fields and ignore_fields:
            raise Exception('Cannot specify both "fields" and "ignore_fields"')
        db = self._db
        fields = ih.get_list_from_arg_strings(fields)
        ignore_fields = ih.get_list_from_arg_strings(ignore_fields)
        if fields:
            kwargs['projection'] = {k: 1 for k in fields}
            if '_id' not in fields:
                kwargs['projection']['_id'] = 0
        if ignore_fields:
            kwargs['projection'] = {k: 0 for k in ignore_fields}
        result = self._client[db][collection].find_one(*args, **kwargs)
        if result is None:
            result = {}
        return result

    def _distinct(self, collection, key, match={}, **kwargs):
        """Return a list of distinct values for key among documents in collection

        - maxTimeMS: max number of milliseconds the operation is allowed to run
        """
        db = self._db
        return self._client[db][collection].distinct(key, match, **kwargs)

    def _count(self, collection, match={}, *args, **kwargs):
        """Return an int

        - match: a dict of the query matching documents to delete
        - maxTimeMS: max number of milliseconds the count_documents operation is
          allowed to run
        - limit: max number of documents to count
        - skip: number of documents to skip before returning results
        - hint: index to use (string, or list of tuples)
        """
        db = self._db
        return self._client[db][collection].count_documents(match, *args, **kwargs)

    def total_documents(self, collection):
        """Return total count of documents in collection"""
        db = self._db
        return self._client[db][collection].estimated_document_count()

    def _aggregate(self, collection, *args, **kwargs):
        """Return a cursor

        - maxTimeMS: max number of milliseconds the aggregate operation is
          allowed to run
        - batchSize: limit number of documents returned in a single batch (> 1)
        - allowDiskUse: if True, allows writing to temporary files in the _tmp
          sub-directory of the --dbpath directory
        """
        db = self._db
        return self._client[db][collection].aggregate(*args, **kwargs)

    def _create_index(self, collection, keys, unique=False, ttl=None,
                      sparse=False, background=False, **kwargs):
        """Create an index on the collection

        - keys: list of 2-item tuples where first item is a field name
          and second item is a direction (1 for ascending, -1 for descending)
            - keys can also be a single key (string) or list of strings
        - unique: if True, create a uniqueness constraint
        - ttl: int representing "time to live" (in seconds) for documents in
          the collection
        - sparse: if True, only index documents that contain the indexed field
        - background: if True, create the index in the background
        - name: custom name to use for the index; auto-generated by default
        - partialFilterExpression: a document that specifies a filter for a
          partial index
        """
        kwargs['unique'] = unique
        kwargs['sparse'] = sparse
        kwargs['background'] = background
        if ttl is not None:
            kwargs['expireAfterSeconds'] = ttl
        db = self._db
        return self._client[db][collection].create_index(keys, **kwargs)

    def _drop_index(self, collection, name, **kwargs):
        """Drop an index from the collection"""
        db = self._db
        return self._client[db][collection].drop_index(name, **kwargs)

    def _drop_indexes(self, collection, **kwargs):
        """Drop all indexes from the collection"""
        db = self._db
        return self._client[db][collection].drop_indexes(**kwargs)

    def _drop_collection(self, collection, **kwargs):
        """Drop a collection from the database"""
        db = self._db
        return self._client[db].drop_collection(collection, **kwargs)

    def _index_information(self, collection):
        """Return a dict of info about indexes on collection"""
        db = self._db
        try:
            index_info = self._client[db][collection].index_information()
        except:
            index_info = {}
        return index_info

    def _index_sizes(self, collection, scale='bytes'):
        """
        - scale: one of bytes, KB, MB, GB

        Wrapper to coll_stats
        """
        return self.coll_stats(collection, scale=scale).get('indexSizes', {})

    def _index_usage(self, collection, name='', full=False):
        """Return list of tuples, sorted by number of operations that used index

        - name: name of specific index
        - full: if True, return full list of dicts from $indexStats aggregation
        """
        db = self._db
        pipeline = [{'$indexStats': {}}]
        if name:
            pipeline.append({'$match': {"name": name}})
        cursor = self._client[db][collection].aggregate(pipeline)
        if full:
            return list(cursor)
        else:
            results = [
                (d['accesses']['ops'], d['name'])
                for d in cursor
            ]
            return sorted(results, reverse=True)

    def last_obj(self, collection, *args, timestamp_field='_id', fields='',
                 ignore_fields='', **kwargs):
        """Return last object inserted to collection

        - args: passed to `self._find_one`
        - timestamp_field: name of timestamp field to sort on
        - fields: string containing fields to return, separated by any of , ; |
        - ignore_fields: string containing fields to ignore, separated by any
          of , ; |
        - kwargs: passed to `self._find_one`
        """
        if 'sort' not in kwargs:
            kwargs['sort'] = [(timestamp_field, -1)]
        return self._find_one(
            collection, *args, fields=fields, ignore_fields=ignore_fields, **kwargs
        )

    def first_obj(self, collection, *args, timestamp_field='_id', fields='',
                  ignore_fields='', **kwargs):
        """Return first object inserted to collection

        - args: passed to `self._find_one`
        - timestamp_field: name of timestamp field to sort on
        - fields: string containing fields to return, separated by any of , ; |
        - ignore_fields: string containing fields to ignore, separated by any
          of , ; |
        - kwargs: passed to `self._find_one`
        """
        if 'sort' not in kwargs:
            kwargs['sort'] = [(timestamp_field, 1)]
        return self._find_one(
            collection, *args, fields=fields, ignore_fields=ignore_fields, **kwargs
        )

    def obj_id_set(self, collection, match):
        """Return set of ObjectIds for match

        - match: dictionary representing the documents to match
        """
        return set([
            x['_id']
            for x in self._find(collection, match, projection=['_id'])
        ])

    def _build_pipeline(self, match=None, group_by=None, timestamp_field='_id',
                    unwind=None, include_array_index=False, projection=None,
                    limit=None, to_set=None, to_list=None, to_sum=None,
                    out=None):
        """Return a list with pipeline stages, to be passed to aggregate method

        - match: dictionary representing the "match stage"
        - group_by: list of keys to group by, or string where items are
          separated by one of , ; |
            - if specified, final grouped results will be ordered by count of
              grouped matches
        - timestamp_field: name of timestamp field to sort on (if 'limit' != None)
          (will sort in descending order to give most recent)
        - unwind: list of keys to unwind (key value in document should be an array),
          or string where items are separated by one of , ; |
        - include_array_index: if True and 'unwind' is specified, the index of each
          unwound item will be included
        - projection: list of keys to project, or string where items are
          separated by one of , ; |
        - limit: max number of items
        - to_set: list of keys, where each key will have its values added to a
          set for each unique group, or string where items are separated by
          one of , ; |
        - to_list: list of keys, where each key will have its values added to a
          list for each unique group, or string where items are separated by
          one of , ; |
        - to_sum: list of keys, where each key will have its values summed
          for each unique group, or string where items are separated by one of
          , ; |
        - out: name of another collection to save results to
        """
        pipeline = []
        group_by = ih.get_list_from_arg_strings(group_by)
        unwind = ih.get_list_from_arg_strings(unwind)
        projection = ih.get_list_from_arg_strings(projection)
        to_set = ih.get_list_from_arg_strings(to_set)
        to_list = ih.get_list_from_arg_strings(to_list)
        to_sum = ih.get_list_from_arg_strings(to_sum)

        if match is not None:
            pipeline.append({'$match': match})

        if limit:
            pipeline.append({'$sort': {timestamp_field: -1}})
            pipeline.append({'$limit': limit})

        if unwind:
            if include_array_index is True:
                for key in unwind:
                    pipeline.append({'$unwind': {
                        'path': '${}'.format(key),
                        'includeArrayIndex': '{}_idx'.format(key)
                    }})
            else:
                for key in unwind:
                    pipeline.append({'$unwind': '${}'.format(key)})

        if projection:
            pipeline.append({'$project': {k: '${}'.format(k) for k in projection}})

        if group_by:
            group = {
                '$group': {
                    '_id': {k: '${}'.format(k) for k in group_by},
                    'count': {'$sum': 1},
                }
            }
        else:
            group = {'$group': {}}

        if to_set:
            group['$group'].update({
                k: {'$addToSet': '${}'.format(k)} for k in to_set
            })

        if to_list:
            group['$group'].update({
                k: {'$push': '${}'.format(k)} for k in to_list
            })

        if to_sum:
            group['$group'].update({
                k: {'$sum': '${}'.format(k)} for k in to_sum
            })

        if group != {'$group': {}}:
            pipeline.append(group)
            pipeline.append({'$sort': {'count': -1}})

        if out and pipeline:
            pipeline.append({'$out': out})

        return pipeline

    def _explain_pipeline(self, collection, pipeline):
        """Return a dict"""
        return self._command('aggregate', collection, pipeline=pipeline, explain=True)

    def copy_collection(self, collection, dest_collection, match={},
                        projection=None, timestamp_field='_id', limit=None):
        """Copy matching documents from one collection to another

        - collection: name of collection
        - dest_collection: name of destination collection
        - match: dictionary representing the "match stage"
        - projection: list of keys to project, or string where items are
          separated by one of , ; |
        - timestamp_field: name of timestamp field to sort on (if 'limit' != None)
          (will sort in descending order to give most recent)
        - limit: max number of items
        """
        pipeline = self._build_pipeline(
            match=match,
            timestamp_field=timestamp_field,
            projection=projection,
            limit=limit,
            out=dest_collection
        )
        return self._aggregate(collection, pipeline)

    def ez_pipeline(self, collection, match, group_by, timestamp_field='_id',
                    unwind=None, include_array_index=False, projection=None,
                    limit=None, to_set=None, to_list=None, to_sum=None,
                    group_action=None, include_condition=None, verbose=False):
        """Build/run an aggregation pipeline to group and count data

        - collection: name of collection
        - match: dictionary representing the "match stage"
        - group_by: list of keys to group by, or string where items are
          separated by one of , ; |
        - timestamp_field: name of timestamp field to sort on (if 'limit' != None)
        - unwind: list of keys unwind (key value in document should be an array),
          or string where items are separated by one of , ; |
        - include_array_index: if True and 'unwind' is specified, the index of each
          unwound item will be included
        - projection: list of keys to project, or string where items are
          separated by one of , ; |
        - limit: max number of items
        - to_set: list of keys, where each key will have its values added to a
          set for each unique group, or string where items are separated by
          one of , ; |
        - to_list: list of keys, where each key will have its values added to a
          list for each unique group, or string where items are separated by
          one of , ; |
        - to_sum: list of keys, where each key will have its values summed
          for each unique group, or string where items are separated by one of
          , ; |

        (After aggregation)
        - group_action: callable that will be mapped over each grouped item
        - include_condition: callable returning a bool to determine if a grouped
          item will be included in returned data
        - verbose: if True, print the generated pipeline command

        Return a dictionary with keys 'counts', 'data', 'total', 'group_by',
        'duration', 'pipeline', and 'total_percent'.
        """
        _start = dh.utc_now_localized()
        group_by = ih.get_list_from_arg_strings(group_by)
        pipeline = self._build_pipeline(
            match=match, group_by=group_by, timestamp_field=timestamp_field,
            unwind=unwind, include_array_index=include_array_index,
            projection=projection, limit=limit, to_set=to_set, to_list=to_list,
            to_sum=to_sum
        )

        if verbose:
            from pprint import pprint
            pprint(pipeline)

        cursor = self._aggregate(collection, pipeline)
        counts = []
        data = {}
        total = 0

        if include_condition is None:
            include_condition = lambda x: True
        elif not callable(include_condition):
            include_condition = lambda x: True

        for item in cursor:
            count = item.pop('count')
            total += count

            if include_condition(item):
                the_group = tuple([item['_id'].get(k, '') for k in group_by])
                with suppress(TypeError):
                    item = group_action(item)
                counts.append((the_group, count))
                data[the_group] = item

        final_counts = {'data': []}
        for name, count in counts:
            final_counts['data'].append((name, count, count/total))

        final_data = OrderedDict()
        for x in final_counts['data']:
            key = x[0]
            final_data[key] = data[key]

        total_percent = sum([x[-1] for x in final_counts['data']])

        _end = dh.utc_now_localized()

        results = {
            'counts': final_counts,
            'data': final_data,
            'total': total,
            'total_percent': total_percent,
            'group_by': tuple(group_by),
            'duration': (_end - _start).total_seconds(),
            'pipeline': pipeline,
        }
        return results
