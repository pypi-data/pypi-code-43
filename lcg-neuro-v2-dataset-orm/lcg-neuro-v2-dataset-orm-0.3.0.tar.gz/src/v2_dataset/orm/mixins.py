from . import Column, types
from sqlalchemy.ext.declarative import declared_attr


class PolymorphicBase:
    """Add support for entity-type hierarchies through `SQLAlchemy joined-table inheritance`_ -- base class.

    A polymorphic column of type :class:`sqlalchemy.types.String` is added, with a polymorphic value set to each derived
    class' name. This mixin should be used for the base class in a hierarchy, whereas derived classes should use
    :class:`PolymorphicDerived`.
    """

    #: Polymorphic disambiguation column.
    type = Column(types.String, nullable=False)

    @declared_attr
    def __mapper_args__(cls):
        return {"polymorphic_on": cls.type, "polymorphic_identity": cls.__name__}


class PolymorphicDerived:
    """Add support for entity-type hierarchies through `SQLAlchemy joined-table inheritance`_ -- derived classes.

    The polymorphic column of type :class:`sqlalchemy.types.String` added by :class:`PolymorphicBase`is set to the
    derived class' name. This mixin should be used for the derived classes in a hierarchy, whereas base classes should
    use :class:`PolymorphicBase`.
    """

    @declared_attr
    def __mapper_args__(cls):
        return {"polymorphic_identity": cls.__name__}


class PrimaryKey:
    """Add an integer primary key :attr:`id` to an entity.

    .. important::
        This class overrides :meth:`v2.orm.ModelBase.__repr__` by omitting the primary key column from the printed
        column name-value pairs. However, if you want this behavior to take effect, you should inherit first from
        :class:`PrimaryKey`, then from a model-base created via :func:`v2.orm.declarative_base`, due to Python's method
        resolution order, in which the left-most base class takes precedence.
    """

    #: Primary key.
    id = Column(types.Integer, primary_key=True)

    def __repr__(self):
        kwargs_str = ", ".join(
            f"{column.name}={getattr(self, column.name)!r}"
            for column in self.columns()
            if column.primary_key is False
        )
        return f"{self.__class__.__name__}({kwargs_str})"
