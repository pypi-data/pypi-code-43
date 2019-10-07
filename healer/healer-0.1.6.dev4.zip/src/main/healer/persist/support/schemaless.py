"""
Replicated wide column store on top of Sqlite

https://en.wikipedia.org/wiki/Bigtable
https://eng.uber.com/schemaless-part-one/
https://github.com/ZuoMatthew/sqlite-schemaless
https://rbmhtechnology.github.io/eventuate/architecture.html
"""

from __future__ import annotations

import abc
import functools
import hashlib
import json
import operator
import re
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Generator
from typing import List
from typing import Mapping
from typing import Optional
from typing import Set
from typing import Type
from typing import Union

import peewee
import playhouse
from playhouse.sqlite_ext import SqliteExtDatabase

# TODO
# from playhouse.pool import PooledSqliteExtDatabase

frozen = dataclass(frozen=True)

# type: row key or colum name
EntryID = Union[str, uuid.UUID]

# type: json data cell value as json type union
JsonBundle = Union[str, int, bool, float, list, dict]

# type: resolved big table record as nested dictionary
JsonBucket = Mapping[str, JsonBundle]


@dataclass(frozen=True, init=False, repr=False)
class NoSqlToken(bytes):
    """
    Global event identity
    """

    def __init__(self, token_bytes:bytes):
        self = token_bytes

    def __repr__(self) -> str:
        return f"⟪{self.hex()}⟫"


class NoSqlTokenField(peewee.BlobField):
    """
    Event identity persistence
    """
    field_type = 'TOKEN'

    def db_value(self, py_val:NoSqlToken) -> bytes:
            return py_val

    def python_value(self, db_val:bytes) -> NoSqlToken:
        return NoSqlToken(db_val)


class NoSqlSupport:
    """
    Utility functions
    """

    json_dumps = functools.partial(json.dumps, separators=(',', ':'))
    json_loads = json.loads

    default_pragmas:List[Tuple] = [
        ('page_size', 1024 * 8),  # bytes
        ('cache_size', 1024 * 8),  # pages
        ('journal_mode', 'wal'),
    ]

    @staticmethod
    def sql_safe(text:str) -> str:
        return re.sub('[^\w]+', '', text)

    @staticmethod
    def make_guid() -> bytes:
        return uuid.uuid4().bytes

    @staticmethod
    def make_row_id() -> str:
        return uuid.uuid4().hex

    @staticmethod
    def make_token() -> NoSqlToken:
        return NoSqlToken(NoSqlSupport.make_guid())

    @staticmethod
    def proper_entry_id(row_id:EntryID) -> str:
        if row_id is None:
            return None
        elif isinstance(row_id, str):
            return row_id
        elif isinstance(row_id, uuid.UUID):
            return row_id.hex
        else:
            raise RuntimeError(f"wong type: {row_id}")

    @staticmethod
    def json_encode(entry:JsonBundle) -> str:
        if isinstance(entry, str):
            return entry
        elif isinstance(entry, dict):
            return NoSqlSupport.json_dumps(entry)
        else:
            raise RuntimeError(f"wrong type: {entry}")

    @staticmethod
    def json_decode(entry:str) -> JsonBundle:
        assert isinstance(entry, str), f"wrong type: {entry}"
        return NoSqlSupport.json_loads(entry)

    @staticmethod
    def record_iterator(
            store:NoSqlStore,
            query:peewee.Query,
        ) -> Generator[NoSqlRecord]:
        "dynamic record bucket builder"
        cur_id:EntryID = None
        bucket:JsonBucket = {}
        # scan start
        for row_id, col_id, bundle in query:
            if cur_id is None:
                cur_id = row_id
            if row_id != cur_id:
                record = NoSqlRecord(store=store, row_id=cur_id, **bucket)
                cur_id = row_id
                yield record
                bucket = {}
            bucket[col_id] = bundle
        # scan finish
        if bucket:
            record = NoSqlRecord(store=store, row_id=cur_id, **bucket)
            cur_id = None
            yield record

    @staticmethod
    def make_stamp() -> float:
        return time.time()

    recursive_tree = lambda : defaultdict(NoSqlSupport.recursive_tree)

    @staticmethod
    def make_recursive_tree(regular_dict:dict) -> defaultdict:
        "convert regular dict into nested defaultdict"
        tree = NoSqlSupport.recursive_tree()
        for key, value in regular_dict.items():
            if isinstance(value, dict):
                value = NoSqlSupport.make_recursive_tree(value)
            tree[key] = value
        return tree

    @staticmethod
    def bundle_filter(bundle:JsonBundle) -> JsonBundle:
        "convert json cell into json tree builder"
        if bundle is None:
            return NoSqlSupport.recursive_tree()
        elif isinstance(bundle, dict):
            return NoSqlSupport.make_recursive_tree(bundle)
        else:
            return bundle  # TODO more types for merge


@frozen
class NoSqlEvent:
    """
    NoSql replicated store change event
    """
    store:str = None  # store name
    action:str = None  # create/delete
    row_id:str = None  # row key
    col_id:str = None  # column name
    bundle:str = None  # json data cell
    token:bytes = None  # global event identity
    stamp:float = None  # global event time stamp


class NoSqlReactor(abc.ABC):
    """
    Trait: store event observer
    """

    store:NoSqlStore = None  # injected

    @abc.abstractmethod
    def react_event(self, event:NoSqlEvent) -> None:
        "sql trigger function: react to record create/delete event"

    def unbind(self) -> None:  # injected
        "observer terminate command"


class NoSqlReplicator(NoSqlReactor, abc.ABC):
    """
    Trait: store replication adapter
    """

    apply_token_set:Set[bytes]  # tell  local vs remote

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_token_set = set()

    def apply_event(self, event:NoSqlEvent) -> None:
        "process incoming replication event"
        self.apply_token_set.add(event.token)  # mark remote
        self.store.apply_event(event)  # inject into store

    def react_event(self, event:NoSqlEvent) -> None:  # override
        "process outgoing replication event"
        if event.token in self.apply_token_set:  # remote mark
            self.apply_token_set.remove(event.token)
            self.react_apply_event(event)
        else:
            self.react_local_event(event)

    @abc.abstractmethod
    def react_apply_event(self, event:NoSqlEvent) -> None:
        "react to remote change event: confirm apply ok"

    @abc.abstractmethod
    def react_local_event(self, event:NoSqlEvent) -> None:
        "react to local change event: forward to remote"


class NoSqlDatabase(SqliteExtDatabase):
    """
    NoSql store on top of Sqlite
    """

    def __init__(self,
            datafile:str,
            pragmas:List=NoSqlSupport.default_pragmas,
            **kwargs
        ):
        super().__init__(database=datafile, pragmas=pragmas, **kwargs)
        self.store_registry = dict()
        self.reactor_registry = defaultdict(list)
        self.register_function(fn=self.react_event, name='react_event')

    def react_event(self,
            store:str,
            action:str,
            row_id:str,
            col_id:str,
            bundle:str,
            stamp:float,
            token:bytes,
        ) -> None:
        "invoked via sql trigger function"
        event = NoSqlEvent(
            store=store,
            action=action,
            row_id=row_id,
            col_id=col_id,
            bundle=bundle,
            token=NoSqlToken(token),
            stamp=stamp,
        )
        reactor_list = self.reactor_registry[store]
        for reactor in reactor_list:
            reactor.react_event(event)

    def bind_reactor(self, store:NoSqlStore, reactor:NoSqlReactor) -> None:
        assert isinstance(store, NoSqlStore), f"need store: {store}"
        assert isinstance(reactor, NoSqlReactor), f"need reactor: {reactor}"
        reactor.store = store
        reactor.unbind = lambda : self.reactor_registry[store.store_name].remove(reactor)
        self.reactor_registry[store.store_name].append(reactor)

    def store(self, store_name:str) -> NoSqlStore:
        assert isinstance(store_name, str), f"need string: {store_name}"
        assert store_name == NoSqlSupport.sql_safe(store_name), f"wrong store name: {store_name}"
        store = NoSqlStore(self, store_name)
        return store

    def ensure_store(self, store_name:str) -> NoSqlStore:
        if not store_name in self.store_registry:
            store = self.store(store_name)
            store.issue_create()
            self.store_registry[store_name] = store
        return self.store_registry[store_name]

    def has_table(self, table_name:str) -> bool:
        return table_name in self.get_tables()


class NoSqlQuery:
    """
    NoSql composable query provider
    """

    def __init__(self,
            index:NoSqlIndex,
            expression:peewee.Expression,
            operations:List=None,
            reverse:bool=False,
         ):
        self.index = index
        self.expression = expression
        self.reverse = reverse
        self.operation_list = operations or []

    def __str__(self):
        expr = self.expression
        return (
            f"NoSqlQuery("
            f"index={self.index}, "
            f"expr=(*,{expr.op},*), "
            f"oper={self.operation_list}, "
            f")"
        )

    def __neg__(self) -> NoSqlQuery:
        copy = self.copy()
        copy.reverse = not self.reverse
        return copy

    def __or__(self, rhs:NoSqlQuery) -> NoSqlQuery:
        copy = self.copy()
        if rhs.index.json_path == self.index.json_path:
            copy.expression = (copy.expression | rhs.expression)
        else:
            copy.operation_list.append((operator.or_, rhs))
        return copy

    def __and__(self, rhs:NoSqlQuery) -> NoSqlQuery:
        copy = self.copy()
        if rhs.index == self.index:
            copy.expression = (copy.expression & rhs.expression)
        else:
            copy.operation_list.append((operator.and_, rhs))
        return copy

    def __iter__(self) -> Generator[NoSqlRecord]:
        query = self.query()
        if self.reverse:
            query = query.order_by(peewee.SQL('1 DESC'))
        else:
            query = query  # .order_by(peewee.SQL('1 ASC'))
        record_iterator = NoSqlSupport.record_iterator(self.index.store, query.tuples())
        for record in record_iterator:
            yield record

    def single(self, mapper:Callable=None) -> Optional[NoSqlRecord]:
        for record in self:
            if mapper:
                return mapper(record)
            else:
                return record
        return None

    def copy(self) -> NoSqlQuery:
        return NoSqlQuery(
            self.index,
            self.expression,
            self.operation_list,
            self.reverse)

    def query(self) -> peewee.Query:
        store_model = self.index.store.content_model
        index_model = self.index.index_model
        query_record = (store_model
             .select(
                store_model.row_id,
                store_model.col_id,
                store_model.bundle,
             )
            .join(index_model, on=(
                (store_model.row_id == index_model.row_id)
            ))
        )
        query = (query_record.where(self.expression))
        for operation, nosql_query in self.operation_list:
            query = operation(query, nosql_query.query())
        return query


class NoSqlIndex:
    """
    NoSql index provider
    """

    def __init__(self,
            store:NoSqlStore,
            col_id:EntryID,
            json_path:str,
        ):
        self.store = store
        self.col_id = NoSqlSupport.proper_entry_id(col_id)
        self.json_path = json_path
        safe_path = NoSqlSupport.sql_safe(json_path)
        self.table_name = f"{store.store_name}_index_{self.col_id}_{safe_path}"
        self.trigger_name_set = set()
        self.configure_model()

    def __str__(self) -> str:
        return (
            f"NoSqlIndex("
            f"store={self.store.store_name}, "
            f"col_id={self.col_id}, "
            f"json_path={self.json_path}, "
            f")"
        )

    def configure_model(self) -> None:
        "define NoSql index SQL schema"

        class IndexModel(peewee.Model):
            # index join key
            row_id = peewee.TextField(index=True, unique=True)
            # big table: data cell json extract
            resource = peewee.TextField(null=True)

            class Meta:
                database = self.store.database
                table_name = self.table_name
                legacy_table_names = False  # https://github.com/coleifer/peewee/issues/1648

        self.index_model = IndexModel

    def entry_list(self) -> peewee.SQL:
        return (self.index_model
                .select(
                    self.index_model.row_id,
                    self.index_model.resource,
                )
                .order_by(self.index_model.row_id)
                .dicts())

    def trigger_name(self, suffix:str) -> str:
        trigger_name = f"{self.table_name}_{suffix}"
        self.trigger_name_set.add(trigger_name)
        return trigger_name

    def trigger_create(self) -> None:
        content_table = self.store.content_table
        index_table = self.table_name
        col_id = self.col_id
        json_path = self.json_path
        #
        trigger_name = self.trigger_name('create')
        trigger_query = (
            f"CREATE TRIGGER IF NOT EXISTS {trigger_name} "
            f"AFTER INSERT ON {content_table} "
            f"FOR EACH ROW "
            f"WHEN ( new.col_id = '{col_id}' "
            f"                    AND json_extract(new.bundle, '{json_path}') IS NOT NULL) "
            f"BEGIN "
                f"INSERT OR REPLACE INTO {index_table} (row_id, resource) "
                f"VALUES (new.row_id, json_extract(new.bundle, '{json_path}')); "
            f"END; "
        )
        self.store.database.execute_sql(trigger_query)
        #
        trigger_name = self.trigger_name('delete')
        trigger_query = (
            f"CREATE TRIGGER IF NOT EXISTS {trigger_name} "
            f"AFTER DELETE ON {content_table} "
            f"FOR EACH ROW "
            f"WHEN ( old.col_id = '{col_id}' ) "
            f"BEGIN "
                f"DELETE FROM {index_table} WHERE "
                f"row_id = old.row_id; "
            f"END; "
        )
        self.store.database.execute_sql(trigger_query)

    def trigger_delete(self) -> None:
        for trigger_name in self.trigger_name_set:
            query = f"DROP TRIGGER IF EXISTS {trigger_name}"
            self.store.database.execute_sql(query)

    def build_index(self):
        content_table = self.store.content_table
        index_table = self.table_name
        col_id = self.col_id
        json_path = self.json_path
        query = (
            f"INSERT INTO {index_table} (row_id, resource) "
            f"SELECT result.row_id, json_extract(result.bundle, '{json_path}') "
            f"FROM {content_table} AS result "
            f"WHERE ("
            f"  result.col_id=? AND json_extract(result.bundle, '{json_path}') IS NOT NULL "
            f") "
        )
        self.store.database.execute_sql(query, [col_id])

    operation_map = {
        '<': operator.lt,
        '<=': operator.le,
        '==': operator.eq,
        '>=': operator.ge,
        '>': operator.gt,
        '!=': operator.ne,
        'LIKE': operator.pow,
        'IN': operator.lshift,
    }

    def query(self,
              expression:Union[str, peewee.Expression],
              operation=operator.eq,
              reverse=False,
        ) -> NoSqlQuery:
        if isinstance(expression, peewee.Expression):
            return NoSqlQuery(self, expression, reverse=reverse)
        if isinstance(operation, str):
            operation = self.operation_map[operation]
        expression = operation(self.index_model.resource, expression)
        return NoSqlQuery(self, expression, reverse=reverse)

#     @staticmethod
#     def query_op(op:str) -> Callable:
#
#         def inner(self, rhs):
#             return self.query(rhs, op)
#
#         return inner

    query_method = lambda op : (lambda self, rhs : self.query(rhs, op))

    __eq__ = query_method('==')
    __ne__ = query_method('!=')
    __gt__ = query_method('>')
    __ge__ = query_method('>=')
    __lt__ = query_method('<')
    __le__ = query_method('<=')


class NoSqlStore:
    """
    NoSql store wide column table.
    """

    def __init__(self,
             database:NoSqlDatabase,
             store_name:str,
             # store row id generator
             make_row_id:Callable[None, str]=NoSqlSupport.make_row_id,
             # store time stamp generator
             make_stamp:Callable[None, float]=NoSqlSupport.make_stamp,
             # store record token generator
             make_token:Callable[None, bytes]=NoSqlSupport.make_token,
         ):
        self.database = database
        self.store_name = store_name
        self.make_row_id = make_row_id
        self.make_stamp = make_stamp
        self.make_token = make_token
        self.content_table = f"{store_name}_content"
        self.journal_table = f"{store_name}_journal"
        self.configure_model()
        self.index_list = []
        self.trigger_name_set = set()

    def bind_reactor(self, reactor:NoSqlReactor) -> None:
        "attach create/delete trigger signal function"
        self.database.bind_reactor(self, reactor)

    def apply_event(self, event:NoSqlEvent) -> None:
        "process incoming external replication event"
        assert event.store == self.store_name, f"wrong store: {event}"
        write_model = self.journal_model
        query = (write_model
            .insert(
                row_id=event.row_id,
                col_id=event.col_id,
                bundle=NoSqlSupport.json_decode(event.bundle),
                token=NoSqlToken(event.token),
                stamp=event.stamp,
                action=event.action,
            )
            # propagate 'replace' from journal to content via trigger
            .on_conflict_replace()  # TODO target
        )
        query.execute()

    def table_digest(self,
            model:peewee.Model,
            time_start:float=None,
            time_finish:float=None,
        ) -> str:
        "produce digest of store table"
        query = (model.select(
                    model.row_id.concat('|')
                    .concat(model.col_id).concat('|')
                    .concat(model.bundle).concat('|')
                    .concat(model.stamp).concat('|')
                    .concat(model.token).concat('|')
                    .cast('BLOB')
                )
                .order_by(model.stamp)
            )
        if time_start:
            query = query.where(time_start <= model.stamp)
        if time_finish:
            query = query.where(model.stamp <= time_finish)
        digest = hashlib.blake2b()
        for entry in query.tuples():
            line = entry[0]
            digest.update(line)
        return digest.hexdigest()

    def content_digest(self, time_start:float=None, time_finish:float=None) -> str:
        "produce digest of store content"
        return self.table_digest(self.content_model, time_start, time_finish)

    def journal_digest(self, time_start:float=None, time_finish:float=None) -> str:
        "produce digest of store journal"
        return self.table_digest(self.journal_model, time_start, time_finish)

    def configure_model(self) -> None:
        "define NoSql store SQL schema"

        class BaseModel(peewee.Model):
            "shared content/journal fields"
            # sqlite row identity
            serial = peewee.AutoField(index=True, unique=True)
            # big table: row key
            row_id = peewee.TextField(index=True)
            # big table: column name
            col_id = peewee.TextField(index=True)
            # big table: data cell in json format
            bundle = playhouse.sqlite_ext.JSONField(
                json_dumps=NoSqlSupport.json_dumps,
                json_loads=NoSqlSupport.json_loads,
            )
            # global event time stamp
            stamp = peewee.FloatField(index=True, default=self.make_stamp)
            # global event identity
            token = NoSqlTokenField(index=True, default=self.make_token)

            class Meta:
                database = self.database
                legacy_table_names = False  # https://github.com/coleifer/peewee/issues/1648

        class ContentModel(BaseModel):
            "content table keeps current snapshot"

            class Meta:
                table_name = self.content_table
                indexes = (
                    (('row_id', 'col_id'), True),
                )

        class JournalModel(BaseModel):
            "journal table keeps change event log"
            # event entry type
            action = peewee.TextField(index=True)

            class Meta:
                table_name = self.journal_table
                indexes = (
                    (('token', 'action'), True),
                )

        self.content_model = ContentModel
        self.journal_model = JournalModel

    def issue_create(self) -> None:
        "command to produce database schema"
        self.content_model.create_table(True)
        self.journal_model.create_table(True)
        self.trigger_create()
        for index in self.index_list:
            index.trigger_create()

    def issue_delete(self) -> None:
        "command to destroy database schema"
        for index in self.index_list:
            index.trigger_delete()
        self.trigger_delete()
        self.journal_model.drop_table()
        self.content_model.drop_table()

    def trigger_name(self, suffix:str) -> str:
        trigger_name = f'{self.store_name}_signal_{suffix}'
        self.trigger_name_set.add(trigger_name)
        return trigger_name

    def trigger_create(self):
        "produce event create/delete/react triggers"
        content_table = self.content_table
        journal_table = self.journal_table
        #
        trigger_name = self.trigger_name('event_create')
        trigger_query = (
        f"CREATE TRIGGER IF NOT EXISTS {trigger_name} "
        f"AFTER INSERT ON '{journal_table}' "
        f"FOR EACH ROW "
        f"WHEN ( 'create' = new.action ) AND "
            f"new.stamp >= ( "  # strategy: latest wins
            f"SELECT COALESCE(MAX(stamp),0) FROM {content_table} "
            f"WHERE row_id = new.row_id AND col_id = new.col_id "
            f") "
        f"BEGIN "
            f"INSERT INTO '{content_table}' (row_id, col_id, bundle, stamp, token) "
            f"VALUES(new.row_id, new.col_id, new.bundle, new.stamp, new.token); "
        f"END; "
        )
        self.database.execute_sql(trigger_query)
        #
        trigger_name = self.trigger_name('event_delete')
        trigger_query = (
        f"CREATE TRIGGER IF NOT EXISTS {trigger_name} "
        f"AFTER INSERT ON '{journal_table}' "
        f"FOR EACH ROW "
        f"WHEN ( 'delete' = new.action ) "
        f"BEGIN "
            f"DELETE FROM '{content_table}' WHERE "
            f"row_id = new.row_id AND col_id = new.col_id; "
        f"END; "
        )
        self.database.execute_sql(trigger_query)
        #
        trigger_name = self.trigger_name('event_react')
        trigger_query = (
        f"CREATE TRIGGER IF NOT EXISTS {trigger_name} "
        f"AFTER INSERT ON '{journal_table}' "
        f"FOR EACH ROW "
        f"BEGIN "
            f"SELECT react_event('{self.store_name}', new.action, "
            f"      new.row_id, new.col_id, new.bundle, new.stamp, new.token); "
        f"END; "
        )
        self.database.execute_sql(trigger_query)

    def trigger_delete(self) -> None:
        "destroy event create/delete/react triggers"
        for trigger_name in self.trigger_name_set:
            query = f"DROP TRIGGER IF EXISTS {trigger_name}"
            self.database.execute_sql(query)

    def __getitem__(self, row_id:EntryID) -> NoSqlRecord:
        "store access by row id"
        return NoSqlRecord(self, row_id)

    def __delitem__(self, row_id:EntryID) -> None:
        "store access by row id"
        NoSqlRecord(self, row_id).delete()

    def get_record(self, row_id:EntryID, col_id_list:List[EntryID]=None) -> NoSqlRecord:
        entry = NoSqlRecord(self, row_id)
        entry.multi_get(col_id_list)
        return entry

    def ensure_record(self, row_id:EntryID=None, **bucket:JsonBucket) -> NoSqlRecord:
        entry = NoSqlRecord(self, row_id, **bucket)
        if bucket:
            entry.multi_set(bucket)
        return entry

    def ensure_index(self, col_id:EntryID, json_path:str) -> NoSqlIndex:
        index = NoSqlIndex(self, col_id, json_path)
        if not self.database.has_table(index.table_name):
            index.index_model.create_table(True)
            index.trigger_create()
            index.build_index()
        self.index_list.append(index)
        return index

    def atomic(self) -> peewee._atomic:
        return self.database.atomic()

    def __iter__(self) -> Generator[NoSqlRecord]:
        return self.record_iterator()

    def record_iterator(self) -> Generator[NoSqlRecord]:
        read_model = self.content_model
        query_record = (read_model
             .select(
                read_model.row_id,
                read_model.col_id,
                read_model.bundle,
             )
            .order_by(read_model.stamp)
        )
        record_iterator = NoSqlSupport.record_iterator(self, query_record.tuples())
        for record in record_iterator:
            yield record


class NoSqlValue(dict):
    ""

#     def __init__(self,
#             record:NoSqlRecord,
#          ):
#         self.record = record

    def __get__(self, key:str) -> JsonBundle:
        print(f"G {key}")

    def __getitem__(self, key:str) -> JsonBundle:
        print(f"GI {key}")
        if key in self:
            pass

    def __setitem__(self, key:str, value:JsonBundle) -> JsonBundle:
        print(f"SI {key} = {value}")
        if key in self:
            pass


class NoSqlRecord:
    """
    Expose nosql store record: selected columns for a given row
    """

    def __init__(self,
            store:NoSqlStore,
            row_id:EntryID=None,
            **bucket:JsonBucket
         ):
        self.store = store
        self.row_id = NoSqlSupport.proper_entry_id(row_id)
        self.bucket = bucket  # always {}

    def __repr__(self):
        return (
            f"Record("
            f"table={self.store.store_name}, "
            f"row_id={self.row_id}, "
            f"bucket={self.bucket}, "
            f")"
        )

    def __getitem__(self, col_id:EntryID) -> JsonBundle:
        return self.solo_get(col_id)

    def __setitem__(self, col_id:EntryID, bundle:JsonBundle) -> None:
        self.solo_set(col_id, bundle)

    def __delitem__(self, col_id:EntryID) -> None:
        self.solo_delete(col_id)

    def solo_get(self, col_id:EntryID, bundle_filter:Callable=None) -> JsonBundle:
        "extract single column bundle; cache values"
        if not self.row_id:
            return None
        col_id = NoSqlSupport.proper_entry_id(col_id)
        if col_id not in self.bucket:
            read_model = self.store.content_model
            query = (read_model
                .select(
                    read_model.bundle,
                )
                .where(
                    (read_model.row_id == self.row_id) &
                    (read_model.col_id == col_id)
                )
            )
            bundle = query.scalar()
            if bundle_filter:
                bundle = bundle_filter(bundle)
            self.bucket[col_id] = bundle
        return self.bucket[col_id]

    def solo_set(self, col_id:EntryID, bundle:JsonBundle, stamp:float=None) -> None:
        "persist single column bundle"
        self.ensure_row_id()
        col_id = NoSqlSupport.proper_entry_id(col_id)
        if bundle:
            self.issue_write('create', self.row_id, col_id, bundle, stamp)
            self.bucket[col_id] = bundle
        else:
            self.solo_delete(col_id, stamp)

    def solo_delete(self, col_id:EntryID, stamp:float=None) -> None:
        "destroy single column bundle; clear cache"
        if not self.row_id:
            return
        col_id = NoSqlSupport.proper_entry_id(col_id)
        self.issue_write('delete', self.row_id, col_id, self.bucket, stamp)
        try:
            del self.bucket[col_id]
        except KeyError:
            pass

    def bundle_load(self, col_id:EntryID) -> JsonBundle:
        "preload json cell with json tree builder"
        return self.solo_get(col_id, NoSqlSupport.bundle_filter)

    def bundle_save(self, col_id:EntryID, stamp:float=None) -> None:
        "persist preloaded json cell back to store"
        self.solo_set(col_id, self.bucket[col_id], stamp)

    def ensure_row_id(self):
        if not self.row_id:
            self.row_id = self.store.make_row_id()

    def issue_write(self,
            action:str,
            row_id:EntryID,
            col_id:EntryID,
            bundle:JsonBundle,
            stamp:float=None,
            ) -> None:
        "make single create/delete entry into journal"
        write_model = self.store.journal_model
        stamp = stamp or self.store.make_stamp()
        query = (write_model
            .insert(
                row_id=row_id,
                col_id=col_id,
                bundle=bundle,
                stamp=stamp,
                action=action,
            )
            # propagate 'replace' from journal to content via trigger
            .on_conflict_replace()  # TODO target
        )
        query.execute()

    def multi_get(self, col_id_list:List[EntryID]=None) -> JsonBucket:
        "extract multi-column bucket; cache values"
        bucket = {}
        if not self.row_id:
            return bucket
        read_model = self.store.content_model
        query = (read_model
            .select(
                read_model.col_id,
                read_model.bundle,
            )
            .where(read_model.row_id == self.row_id)
        )
        if col_id_list:
            query = query.where(read_model.col_id.in_(col_id_list))
        for col_id, bundle in query.tuples():
            bucket[col_id] = bundle
            self.bucket[col_id] = bundle
        return bucket

    def multi_set(self, bucket:JsonBucket, stamp:float=None) -> None:
        "persist multi-column bucket"
        self.ensure_row_id()
        if bucket:
            self.issue_multi_write('create', self.row_id, bucket, stamp)
            self.bucket = bucket
        else:
            self.multi_delete(stamp)

    def multi_delete(self, stamp:float=None) -> None:
        self.issue_multi_write('delete', self.row_id, self.bucket, stamp)
        self.bucket = {}

    def issue_multi_write(self,
            action:str,
            row_id:EntryID,
            bucket:JsonBucket,
            stamp:float=None,
        ) -> None:
        "make multiple create/delete entries into journal"
        stamp = stamp or self.store.make_stamp()
        entry_list = [
            dict(
                row_id=row_id,
                col_id=col_id,
                bundle=bundle,
                stamp=stamp,
                action=action,
            )
            for col_id, bundle in bucket.items()
        ]
        write_model = self.store.journal_model
        query = (write_model
            .insert_many(rows=entry_list)
            # propagate 'replace' from journal to content via trigger
            .on_conflict_replace()  # TODO target
        )
        query.execute()

    def multi_get_on_empty(self):
        if self.row_id and not self.bucket:
            self.multi_get()

    def keys(self):
        "iterate col_id in the record"
        self.multi_get_on_empty()
        return self.bucket.keys()

    def values(self):
        "iterate bundle in the record"
        self.multi_get_on_empty()
        return self.bucket.values()

    def items(self):
        "iterate (col_id, bundle) in the record"
        self.multi_get_on_empty()
        return self.bucket.items()

    def to_event(self, action:str, col_id:EntryID, stamp:float=None) -> NoSqlEvent:
        "render single column bundle as replication event"
        if not self.row_id:
            return None
        if not col_id in self.bucket:
            return None
        stamp = stamp or self.store.make_stamp()
        token = self.store.make_token()
        store = self.store.store_name
        row_id = self.row_id
        bundle = NoSqlSupport.json_encode(self.bucket[col_id])
        event = NoSqlEvent(
            store=store,
            action=action,
            row_id=row_id,
            col_id=col_id,
            bundle=bundle,
            token=token,
            stamp=stamp,
        )
        return event

    def to_event_list(self, action:str, stamp:float=None) -> List[NoSqlEvent]:
        "render multi-column bucket as replication event list"
        event_list = []
        if not self.row_id:
            return event_list
        if not self.bucket:
            return event_list
        for col_id in self.keys():
            event = self.to_event(action, col_id, stamp)
            event_list.append(event)
        return event_list
