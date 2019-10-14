"""Basic tools for defining entity classes.
"""

from v2_dataset.orm import declarative_base

#: `SQLAlchemy declarative base`_ (created by :func:`v2.orm.declarative_base`) from which all entity-types in the
#: :mod:`v2.db.model` package are derived.
Model = declarative_base()
