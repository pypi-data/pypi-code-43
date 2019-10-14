"""This module helps in declaring the entity classes and their relationships in other submodules of this package (as
:mod:`v2_dataset.db`, for instance). Entity-types are declared by extending from a `SQLAlchemy declarative base`_ class ---
which maps objects in a Python class hierarchy to rows in a SQL database --- created by :func:`declarative_base`, which
returns a model base-class (with additional properties defined in :class:`ModelBase`) that can be used to define
entity-types. For example:

.. code:: python

    from v2_dataset.orm import Column, declarative_base, types

    Model = declarative_base()

    class SomeEntity(Model):
        id = Column(types.Integer, primary_key=True)
        name = Column(types.String)

The set of features in this module include:

* :func:`StrictForeignKey` is an alias for foreign with ``ON UPDATE CASCADE ON DELETE RESTRICT`` SQL behavior.
* :func:`declarative_base` creates `SQLAlchemy declarative base`_ classes with some characteristics:

    * Derived entity-types:

        * Have corresponding tables named after their ``__name__`` attributes,
        * Get a default ``__repr__`` method,
        * Get a convenience ``compare`` method for checking for equality of instantiated objects, possibly
          ignoring the primary key,
        * Have a ``columns`` class-method that returns the list of declared columns, and
        * Get the ability to inherit from Python-style :mod:`abc` interfaces in entity classes, allowing ORM entity
          classes to fulfill interfaces.

    * The model-base provides :meth:`ModelBase.relate_1_to_n` and :meth:`ModelBase.relate_m_to_n` methods that help in
      declaring reciprocal relationships between entity types.

* A custom :class:`Query` class that provides the :meth:`Query.all_scalars` method for fetching results from queries on
  columns as a list of values, rather than a list of length 1 tuples (raises :exc:`MultipleScalarsFound` on error), and
* A modified :class:`sessionmaker` factory-type for creating database session factories bound to this custom query class
  (replaces :class:`sqlalchemy.orm.session.sessionmaker`).

All SQLAlchemy column types, plus some extension types, are provided by the :mod:`v2_dataset.orm.types` module. Any
other required SQLAlchemy_ functionality not patched by this package (like constraints and query operators), should be
imported directly from :mod:`sqlalchemy` and its sub-modules.
"""
import abc
import numpy
import sqlalchemy.orm
import textwrap

from sqlalchemy import Column, ForeignKey, Table as _Table
from sqlalchemy.ext.declarative import (
    DeclarativeMeta as _DeclarativeMeta,
    declarative_base as _declarative_base,
    declared_attr,
)
from sqlalchemy.orm import relationship, sessionmaker as _sessionmaker


def StrictForeignKey(*args, **kwargs):
    """Alias for :class:`sqlalchemy.ForeignKey` that cascades updates and forbids removal of objects referred elsewhere.

    In other words, ``StrictForeignKey(*args, **kwargs)`` corresponds to::

        ForeignKey(*args, **kwargs, onupdate='CASCADE', ondelete='RESTRICT')

    """
    kwargs.update({"onupdate": "CASCADE", "ondelete": "RESTRICT"})
    return ForeignKey(*args, **kwargs)


def declarative_base(**kwargs):
    """Forwards arguments to :func:`sqlalchemy.ext.declarative.declarative_base`, setting the model base's type (``cls``
    argument) to :class:`ModelBase` and name (``name`` argument) to ``'Model'``. Use this function to create a base
    class for all model classes in your ORM module.
    """
    kwargs.update({"name": "Model", "cls": ModelBase, "metaclass": DeclarativeMeta})
    model_class = _declarative_base(**kwargs)
    return model_class


class DeclarativeMeta(_DeclarativeMeta, abc.ABCMeta):
    """Custom declarative metaclass that allows to inherit from :mod:`abc` interfaces in entity classes.
    """

    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        if bases != (ModelBase,):
            new_class.model_classes[name] = new_class
        return new_class


class ModelBase:
    """Defines default properties and additional operations available on all ORM entity-types derived from the
    `SQLAlchemy declarative base`_ class returned by :func:`declarative_base`, *i.e.* all entity-types defined in this
    package. The following functionality is provided:

    * Tables are automatically named after the derived entity-class (override :meth:`__tablename__` with
      :class:`sqlalchemy.ext.declarative.declared_attr` if you must change it),
    * The :attr:`model_classes` class-attribute provides access to derived entity-types, similar to how :attr:`tables`
      provides access to corresponding :class:`sqlalchemy.sql.schema.Table`.
    * The :meth:`columns` class-method lists all columns defined on an entity-type,
    * The :meth:`compare` method helps in testing equality between instances, even if they belong to different sessions,
      by looking at column values (possibly ignoring primary keys),
    * A modified :meth:`__eq__` method that is a shortcut for calling :meth:`compare` with ``ignore_pk=False``,
    * A default :meth:`__repr__` (which prints all column name-value pairs in :class:`dict`-form) is provided, and
    * Class-methods :meth:`relate_1_to_n` and :meth:`relate_m_to_n` may be used to define reciprocal relationships on
      entity-type pairs (by creating additional attributes on each class and tables as needed), and
    * A convenience :meth:`query` class-method allows to run queries on an specific entity-type, using `SQLAlchemy
      scoped sessions`_.
    """

    #: Class-attribute dictionary that maps derived model-class names to model-class.
    model_classes = {}

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__

    @classmethod
    def columns(cls):
        """Convenience method for obtaining the columns of this entity type.

        :rtype: dict
        """
        return cls.metadata.tables[cls.__tablename__].columns

    @classmethod
    def relate_1_to_n(
        cls,
        entity_1,
        entity_n,
        prop_1,
        prop_n,
        doc_1=None,
        doc_n=None,
        side1_kwargs=None,
        side2_kwargs=None,
    ):
        """Create an 1-to-N relationship between two entity types. N may also be 1.

        Corresponding relationship properties (:func:`sqlalchemy.orm.relationship`) for accessing the complementary sides of
        the relationship are added to each entity class.

        Parameters
        ----------
        entity_1: type
            A SQLAlchemy_ entity-class (derived from this base) that represents the 1-side of the relationship.

        entity_n: type
            A SQLAlchemy_ entity-class (derived from this base) that represents the N-side of the relationship.

        prop_1: str
            Name of the relationship property that is added to the ``entity_1`` entity class in order to access related
            ``entity_n`` values.

        prop_n: str
            Name of the relationship property that is added to the ``entity_n`` entity class in order to access related
            ``entity_m`` values.

        doc_1: str, optional
            Docstring for the class attribute ``prop_1`` that is created in class ``entity_1``. A default docstring is
            created if none is provided.

        doc_n: str, optional
            Docstring for the class attribute ``prop_1`` that is created in class ``entity_n``. A default docstring is
            created if none is provided.

        side1_kwargs: dict, optional
            Additional keyword arguments to pass to :func:`sqlalchemy.relationship`, when called on ``entity_1``.

        side2_kwargs: dict, optional
            Additional keyword arguments to pass to :func:`sqlalchemy.relationship`, when called on ``entity_2``.
        """
        side1_kwargs = {
            **{"cascade": "all, delete, delete-orphan"},
            **(side1_kwargs or {}),
        }
        side2_kwargs = side2_kwargs or {}

        setattr(
            entity_1,
            prop_1,
            relationship(entity_n, back_populates=prop_n, **side1_kwargs),
        )
        setattr(
            entity_n,
            prop_n,
            relationship(entity_1, back_populates=prop_1, **side2_kwargs),
        )

        if doc_1 is None:
            doc_1 = textwrap.dedent(
                "SQLAlchemy relationship that maps to a list of related :class:`{}.{}` objects.".format(
                    entity_n.__module__, entity_n.__name__
                )
            )

        if doc_n is None:
            doc_n = textwrap.dedent(
                "SQLAlchemy relationship that maps to the corresponding :class:`{}.{}` object.".format(
                    entity_1.__module__, entity_1.__name__
                )
            )

        getattr(entity_1, prop_1).__doc__ = doc_1
        getattr(entity_n, prop_n).__doc__ = doc_n

    @classmethod
    def relate_m_to_n(
        cls,
        entity_m,
        entity_n,
        prop_m,
        prop_n,
        relation_name=None,
        key_m=None,
        key_n=None,
        doc_m=None,
        doc_n=None,
        relationship_kwargs=None,
    ):
        """Creates an M-to-N relationship between two entity types through a relation table that contains no extra fields.

        Corresponding relationship properties (:func:`sqlalchemy.orm.relationship`) for accessing the complementary sides of
        the relationship are added to each entity class.

        Parameters
        ----------
        entity_m: type
            A SQLAlchemy_ entity-class (derived from this base) that represents the M-side of the relationship.

        entity_n: type
            A SQLAlchemy_ entity-class (derived from this base) that represents the N-side of the relationship.

        relation_name: str, optional
            The name of the M-to-N relation table. If omitted, defaults to::

                entity_m.__name__ + entity_n.__name__

        prop_m: str
            Name of the relationship property that is added to the ``entity_m`` entity class in order to access related
            ``entity_n`` values.

        prop_n: str
            Name of the relationship property that is added to the ``entity_n`` entity class in order to access related
            ``entity_m`` values.

        key_m: :class:`sqlalchemy.Column` or str
            Primary key column from ``entity_m``. If omitted, defaults to::

                getattr(entity_m, 'id')

        key_n: :class:`sqlalchemy.Column` or str
            Primary key column from ``entity_n``. If omitted, defaults to::

                getattr(entity_n, 'id')

        doc_m: str, optional
            Docstring for the class attribute ``prop_1`` that is created in class ``entity_1``

        doc_n: str, optional
            Docstring for the class attribute ``prop_1`` that is created in class ``entity_n``

        relationship_kwargs: dict, optional
            Additional keyword arguments to pass to :func:`sqlalchemy.relationship`.
        """
        relationship_kwargs = relationship_kwargs or {}

        if relation_name is None:
            relation_name = entity_m.__name__ + entity_n.__name__

        if key_m is None:
            key_m = getattr(entity_m, "id")

        if key_n is None:
            key_n = getattr(entity_n, "id")

        relation_entity = _Table(
            relation_name,
            entity_m.metadata,
            Column(
                "{}_id".format(entity_m.__name__.lower()),
                StrictForeignKey(key_m),
                primary_key=True,
            ),
            Column(
                "{}_id".format(entity_n.__name__.lower()),
                StrictForeignKey(key_n),
                primary_key=True,
            ),
        )
        setattr(
            entity_m,
            prop_m,
            relationship(
                entity_n,
                back_populates=prop_n,
                secondary=relation_entity,
                **relationship_kwargs,
            ),
        )
        setattr(
            entity_n,
            prop_n,
            relationship(
                entity_m,
                back_populates=prop_m,
                secondary=relation_entity,
                **relationship_kwargs,
            ),
        )

        if doc_m is None:
            doc_m = textwrap.dedent(
                "SQLAlchemy relationship that maps to a list of related :class:`{}.{}` objects.".format(
                    entity_n.__module__, entity_n.__name__
                )
            )

        if doc_n is None:
            doc_n = textwrap.dedent(
                "SQLAlchemy relationship that maps to a list of related :class:`{}.{}` objects.".format(
                    entity_m.__module__, entity_m.__name__
                )
            )

        getattr(entity_m, prop_m).__doc__ = doc_m
        getattr(entity_n, prop_n).__doc__ = doc_n

    def __eq__(self, other):
        result = self.compare(other, ignore_pk=False)
        return result

    def __repr__(self):
        kwargs_str = ", ".join(
            f"{column.name}={getattr(self, column.name)!r}" for column in self.columns()
        )
        return f"{self.__class__.__name__}({kwargs_str})"

    def compare(self, other, ignore_pk=False):
        """A convenience method for comparing instances of this class.

        :param other: Instance of the same type.
        :param bool ignore_pk: Whether to ignore primary key columns in the comparison.
        :rtype: bool
        """
        result = all(
            numpy.all(getattr(self, column.name) == getattr(other, column.name))
            for column in self.columns()
            if not (ignore_pk and column.primary_key)
        )
        return result


class MultipleScalarsFound(ValueError, sqlalchemy.orm.exc.MultipleResultsFound):
    """Exception raised by :meth:`Query.all_scalar` when multiple scalar values are found in a single result row.
    """


class Query(sqlalchemy.orm.query.Query):
    """Custom SQLAlchemy query class that provides an additional :meth:`all_scalars` method combining the semantics of
    :meth:`sqlalchemy.orm.exc.Query.all` and :meth:`sqlalchemy.orm.exc.Query.scalar`.
    """

    def all_scalars(self):
        """Return an iterable of all scalar, singleton element values from rows matched by this query.

        Raises
        ------
        MultipleScalarsFound: If result rows have more than one element.
        """
        try:
            return [x for (x,) in self.all()]
        except ValueError as e:
            raise MultipleScalarsFound(str(e))


class sessionmaker(_sessionmaker):
    """Extends the :class:`sqlalchemy.orm.session.sessionmaker` session factory maker by automatically binding to the
    extended query class (:class:`Query`)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, query_cls=Query, **kwargs)
