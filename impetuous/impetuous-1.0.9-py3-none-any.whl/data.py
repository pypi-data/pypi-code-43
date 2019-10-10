# TODO rename to tables.py or something?
import logging
import os
import uuid
from datetime import datetime, time, timezone
from pathlib import Path
from shutil import copyfile

import attr
import yaml
from sqlalchemy import (DDL, CheckConstraint, Column, ForeignKey, Index,
                        Integer, MetaData, String, Table, UniqueConstraint,
                        create_engine, types)
from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy.event import listen
from sqlalchemy.exc import DontWrapMixin
from sqlalchemy.sql.expression import join

DEFAULT_DATA_PATH = Path.home() / '.local' / 'share' / 'impetuous' / 'data.sqlite'
DATA_PATH = os.environ.get('IM_DB', DEFAULT_DATA_PATH)

logger = logging.getLogger(__name__)

try:
    from yaml import CSafeLoader as yaml_Loader
    from yaml import CSafeDumper as yaml_Dumper
except ImportError:
    logger.info("I couldn't import C yaml stuff so yaml will be slow.")
    from yaml import SafeLoader as yaml_Loader
    from yaml import SafeDumper as yaml_Dumper


def ensure_sane(engine):
    database = engine.url.database
    if database.lower() != ':memory:':  # What of other special values?
        dbdir = Path(database).parent
        try:
            dbdir.mkdir(parents=True)
        except FileExistsError:
            pass
        else:
            logger.info(_("I made %s for the database to live in because it didn't exist."), dbdir.parent)

    # Auto upgrade
    import alembic.config
    import alembic.command
    alembic_cfg = alembic.config.Config()
    alembic_cfg.set_main_option('script_location', 'impetuous:migrations')
    if (database.lower() != ':memory:' and Path(database).exists()):
        # Detect a special case where the database kinda exists but the version
        # isn't set because early on we made the database before using alembic.
        from alembic.migration import MigrationContext
        from alembic.autogenerate import compare_metadata
        mc = MigrationContext.configure(engine.connect())
        if mc.get_current_revision() is None:
            old_metadata = MetaData()
            Table(
                'entry', old_metadata,
                Column('id', UUID, default=uuid.uuid4, primary_key=True),
                Column('rev', UUID, default=uuid.uuid4, onupdate=uuid.uuid4, nullable=False),
                Column('text', String, nullable=False),
                Column('comment', String, nullable=False, default=''),
                Column('start', UTCDateTime, nullable=False),
                Column('end', UTCDateTime),
                Index('idx_entry_start', 'start', unique=True),
                CheckConstraint('end > start', name='ends after start'),
            )
            Table(
                'submission', old_metadata,
                Column('id', UUID, default=uuid.uuid4, primary_key=True),
                Column('rev', UUID, default=uuid.uuid4, onupdate=uuid.uuid4, nullable=False),
                Column('entry', UUID, ForeignKey('entry.id'), nullable=False),
                Column('ext', String, nullable=False),
                Column('key', String, nullable=False),
                Column('result', YamlDoc, nullable=False),
                Index('idx_submission_entry_ext', 'entry', 'ext', 'key', unique=True),
            )
            diff = compare_metadata(mc, old_metadata)
            if not diff:
                alembic.command.stamp(alembic_cfg, 'f4aaf1bdf8c0')

        # Check if an upgrade is required ...
        from alembic.script import ScriptDirectory
        revision_map = ScriptDirectory.from_config(alembic_cfg).revision_map
        try:
            next(revision_map.iterate_revisions('head', mc.get_current_revision()))
        except StopIteration:
            pass
        else:
            logger.warning("I'm about to migrate your data. You have 3ms to back up %s.", database)
            backup = _make_backup(database)
            logger.warning("Just kidding, a backup has been written to %s.", backup)

    alembic.command.upgrade(alembic_cfg, 'head')


def _make_backup(filepath):
    from impetuous.sheet import utcnow
    copyto = filepath + "." + utcnow().strftime("%Y%m%d_%H%M%S")
    while True:
        try:
            open(copyto, 'xb')
        except FileExistsError:
            copyto += "~"
        else:
            break
    copyfile(filepath, copyto)
    return copyto


def soften_datetime(dt):
    """
    Zeros the microseconds on a datetime so that it resolution is at seconds,
    which is required to store the data.
    """
    return dt.replace(microsecond=0)


class UUID(types.TypeDecorator):
    ''' UUID convenience type for SQLite.
    '''

    impl = types.BLOB

    def process_bind_param(self, value, dialect):
        return None if value is None else value.bytes

    def process_result_value(self, value, dialect):
        return None if value is None else uuid.UUID(bytes=value)


class InvalidDateTime(ValueError, DontWrapMixin):
    pass


class Time(types.TypeDecorator):
    impl = INTEGER

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        else:
            assert value.tzinfo is None
            assert value.microsecond == 0
            return value.hour * 3600 + value.minute * 60 + value.second

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        else:
            minute, second = divmod(value, 60)
            hour, minute = divmod(minute, 60)
            return time(hour=hour, minute=minute, second=second)


class UTCDateTime(types.TypeDecorator):
    ''' DateTime stored as UTC in database, timezone aware in application
    '''
    impl = INTEGER

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        elif hasattr(value, 'tzinfo'):  # duck typing???
            if value.tzinfo != timezone.utc:
                value = value.astimezone(timezone.utc)
            if value.microsecond != 0:
                raise InvalidDateTime("Seconds are the lowest resolution of time supported. This has %d microseconds." % value.microsecond)
            return value.timestamp()
        else:
            raise InvalidDateTime("Excepted a timezone-aware datetime, not a %s." % (type(value).__name__,))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        else:
            # what about utcfromtimestamp? 🤔
            return datetime.fromtimestamp(value, tz=timezone.utc)


class YamlDoc(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value, dialect):
        """ Return an object for inserting nito the database
        """
        if value is None:
            return None
        else:
            return yaml.dump(value, indent=2, default_flow_style=False, Dumper=yaml_Dumper)

    def process_result_value(self, value, dialect):
        """ Return a python object from a database value
        """
        if value is None:
            return None
        else:
            return yaml.load(value, Loader=yaml_Loader)


metadata = MetaData()

entry_t = Table(
    'entry', metadata,
    Column('id', UUID, default=uuid.uuid4, primary_key=True),
    # TODO this should auto update with a trigger or something ...
    Column('rev', UUID, default=uuid.uuid4, onupdate=uuid.uuid4, nullable=False),
    Column('text', String, nullable=False),
    Column('comment', String, nullable=False, default=''),
    Column('start', UTCDateTime, nullable=False),
    Column('end', UTCDateTime),
    Index('idx_entry_start', 'start', unique=True),
    Index('idx_entry_end', 'end'),
    # TODO store date times as big integers or floats or something...
    CheckConstraint('end > start', name='ends after start'),
)

submission_t = Table(
    'submission', metadata,
    Column('id', UUID, default=uuid.uuid4, primary_key=True),
    Column('rev', UUID, default=uuid.uuid4, onupdate=uuid.uuid4, nullable=False),
    # TODO read this http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#foreign-key-support
    Column('entry', UUID, ForeignKey('entry.id'), nullable=False),
    Column('ext', String, nullable=False),
    Column('key', String, nullable=False),
    Column('result', YamlDoc, nullable=False),
    Index('idx_submission_entry_ext', 'entry', 'ext', 'key', unique=True),
)

joins = {
    'entry submissions': join(entry_t, submission_t, entry_t.c.id == submission_t.c.entry),
    'submission entries': join(submission_t, entry_t, entry_t.c.id == submission_t.c.entry),
}

tables = {
    'entry': entry_t,
    'submission': submission_t,
}

SQLDIR = Path(__file__).parent / 'sql'


def read_ddl(name):
    return DDL((SQLDIR / name).open().read())


listen(entry_t, "after_create", read_ddl('check_insert_entry_dtrange.sql'))
listen(entry_t, "after_create", read_ddl('check_update_entry_dtrange.sql'))
