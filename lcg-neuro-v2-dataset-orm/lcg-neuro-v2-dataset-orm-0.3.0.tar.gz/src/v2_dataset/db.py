"""This package provides access to the experimental database. It consists in curated, static information initialized by
the :func:`init_db` function, and experimental, dynamic information manipulated via Python, command-line interface
(:mod:`v2.db.__main__`), or the REST API (:mod:`v2.server`). ORM entity types are defined in :mod:`v2.db.model`, and the
unstable command-line interface is provided in :mod:`v2.db.__main__`. To query/manipulate this database from Python, use
the :data:`engine` global attribute and the :data:`Session`, or :data:`ScopedSession` session factories defined here.
"""

import csv
import datetime
import environ
import iso8601
import packaging
import pathlib
import sqlalchemy.orm.exc
import sqlalchemy.orm.query
import stringcase

from tqdm.autonotebook import tqdm
from v2_dataset import (
    compatible_dataset_version_range,
    config as v2_dataset_config,
    orm,
    model,
)

# _prefix = '_'.join(__name__.upper().split('.')[:-1])
_prefix = "v2_dataset_db"


def _raise(exception):
    raise exception


@environ.config(prefix=_prefix)
class Config:
    """Environment configuration required by this package, specified declaratively via environ_config_.
    """

    #: Auto-initialize the database with curated data.
    auto_init: bool = environ.var(default=False, converter=bool)

    #: Echo SQL statements produced by SQLAlchemy_.
    echo: bool = environ.var(default=False, converter=bool)

    #: Path to SQLite_ database that describes the dataset.
    path: pathlib.Path = environ.var(
        default=v2_dataset_config.dataset_dir / "index.sqlite",
        converter=lambda path: pathlib.Path(path).resolve() if path else path,
        validator=lambda self, attribute, path: _raise(FileNotFoundError(path))
        if (not pathlib.Path(path).parent.is_dir())
        else None,
    )


class Database:
    """Allows to create, initialize, and manipulate concrete databases with the V2 Dataset's ORM model and curated
    information. The :attr:`v2_dataset.compatible_dataset_version_range` attribute is used to check for a compatible
    dataset version during instantiation.

    .. attribute:: engine sqlalchemy.engine.Engine

        Concrete `SQLAlchemy engine`_ for accessing the database.

    .. attribute:: scoped_session sqlalchemy.orm.scoped.scoped_session

        Use this `SQLAlchemy session`_ object/factory instead of :meth:`session` if you need thread-safe session
        objects. Provides access to :class:`sqlalchemy.orm.session.Session` methods and, when called, generates objects
        of type :class:`sqlalchemy.orm.session.Session` with overridden settings. By default, it has auto-flushing
        disabled.
    """

    def __init__(self, conn_string=None, init=None, engine_params=None):
        conn_string = conn_string or f"sqlite:///{config.path}"
        engine_params = {**{"echo": config.echo}, **(engine_params or {})}
        self.engine = sqlalchemy.create_engine(conn_string, **engine_params)
        self._session_factory = orm.sessionmaker(bind=self.engine, autoflush=False)
        self.scoped_session = sqlalchemy.orm.scoped_session(self._session_factory)

        dataset_version = packaging.version.parse(
            open(v2_dataset_config.dataset_dir / "VERSION.txt", "r").read().strip()
        )

        if not (
            compatible_dataset_version_range[0]
            <= dataset_version
            < compatible_dataset_version_range[1]
        ):
            raise RuntimeError(
                f'V2 Dataset version "{dataset_version}" is not compatible with library '
                f"(>={compatible_dataset_version_range[0]}, <{compatible_dataset_version_range[1]})."
            )

        if init or (init is None and config.auto_init):
            self.init()

    def init(self, curated_dir=None):
        """Initialize the database with curated information.

        This method creates all pending tables, then initializes the database with curated retrieved from CSV files. The
        CSV files should be named after the corresponding ORM-mapped entities in *snake-case*. For example, a file named
        ``recording_session.csv`` would be used to insert rows into the SQL table corresponding to the
        :class:`v2_dataset.model.RecordingSession` entity-type.

        curated_dir: str or pathlib.Path, optional
            Path to directory with initialization files. If not provided, defaults to a directory named ``curated``
            inside the directory pointed by :attr:`v2_dataset.config.dataset_dir`.
        """

        curated_dir = pathlib.Path(
            curated_dir or v2_dataset_config.dataset_dir / "tables"
        )

        entity_types = {
            entity_name.upper(): entity_type
            for entity_name, entity_type in model.Model._decl_class_registry.items()
        }

        model.Model.metadata.create_all(self.engine)
        session = self.session()
        for table_path in tqdm(curated_dir.glob("*.csv"), desc="Initializing database"):
            table_name = stringcase.capitalcase(stringcase.camelcase(table_path.stem))
            entity_type = entity_types[table_name.upper()]
            with open(table_path) as table_file:
                table_reader = csv.DictReader(table_file)
                for i, row in enumerate(table_reader):
                    columns = {}
                    for key, val in row.items():
                        if val == "":
                            val = None
                        try:
                            key_parts = key.split("_")
                            if "date" in key_parts or "datetime" in key_parts:
                                val = iso8601.parse_date(val)
                            elif "time" in key_parts:
                                # TODO: Could replace by datetime.time.fromisoformat(val) in Python 3.7.
                                time_parts = val.split(":")
                                val = datetime.time(
                                    hour=int(time_parts[0]),
                                    minute=int(time_parts[1]),
                                    second=int(time_parts[2].split(".")[0]),
                                    microsecond=int(time_parts[2].split(".")[1]),
                                )
                            if key != "id":
                                columns[key] = val
                        except (ValueError, iso8601.ParseError) as exc:
                            raise Exception(
                                f"Parsing failed for entity-type column '{table_name}.{key}: {val}' from '{table_path!s}:{i + 1}': {exc}"
                            )
                    try:
                        entity = entity_type(**columns)
                        session.add(entity)
                    except (TypeError, sqlalchemy.exc.StatementError) as exc:
                        raise Exception(
                            f"Insert failed for entity-type '{table_name}' with data from '{table_path!s}:{i + 1}': {exc}"
                        )
        session.commit()

    def query(self, entity_type):
        """Shortcut for calling :meth:`sqlalchemy.orm.Session.query` on :attr:`scoped_session`.

        Parameters
        ----------
        entity_type: type
            An entity-type, a subclass of :class:`v2_dataset.model.Model`.

        Examples
        --------
        Suppose a database is created with

        .. code:: python

            from v2_dataset import model, db

            database = db.Database(init=True)

        then calling

        .. code:: python

            database.query(model.Recording).filter_by(...)

        is the same as

        .. code:: python

            database.scoped_session.query(model.Recording).filter_by(...)
        """
        return self.scoped_session.query(entity_type)

    def session(self, **kwargs):
        """Creates a new `SQLAlchemy session`_ that may be used for querying/making chages to the database. Use this
        session factory to open SQLAlchemy_ sessions to query/manipulate the database. When called, generates objects of
        type :class:`sqlalchemy.orm.session.Session`, forwarding any keyword-arguments given. By default, it has
        auto-flushing disabled.

        Returns
        -------
        session: sqlalchemy.orm.session.Session
        """
        return self._session_factory(**kwargs)


#: Contains the environment configuration required by :mod:`v2.db`.
config: Config = environ.to_config(Config)
