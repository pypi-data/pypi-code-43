import typing
from inspect import getmro


class ElementSchemaMeta(type):
    def __new__(cls, name, parents, dct):
        __props__ = {}
        for parent in parents:
            classes = reversed(getmro(parent))
            for klass in classes:
                __props__.update(getattr(klass, "__annotations__", {}))
        __props__.update(dct.get("__annotations__", {}))
        __props__.pop("_name_")
        dct["_name_"] = dct.get("_name_", name.lower())
        dct["__props__"] = __props__
        return super().__new__(cls, name, parents, dct)


class ElementSchema(metaclass=ElementSchemaMeta):
    """Class that defines the schema for a particular element in your
    settings heirarchy. Subclass this and add annotations to define
    the allowed values for this element type-

    .. code-block:: python

        class Element(ElementSchema):
            color: str
            height: int

    """

    _name_: str = ""
    _manager_ = None
    _klass_ = None
    _id_ = None
    _ctx_ = None
    _allowextra_ = False

    def __init__(self, configManager):
        self._manager_ = configManager

    def __call__(self, name=None, identifier=None, ctx=None):
        self._klass_ = name
        self._id_ = identifier
        self._ctx_ = ctx
        return self

    @property
    def context(self):
        """The context stack that will be used to look up settings for this object"""
        if self._ctx_:
            return self._ctx_
        base = self._name_
        if self._klass_:
            base += f".{self._klass_}"
        if self._id_:
            base += f"#{self._id_}"
        return base

    def __getattr__(self, item):
        with self._manager_.context(self.context):
            return getattr(self._manager_, item)

    def load(self):
        """Loads the settings for this schema into a python dictionary. Looks up the value for
        each property using the current context stack for this object.

        .. note::

            This will throw an error if there are settings defined on the schema that can't be
            found in any level!
        """
        return {key: getattr(self, key) for key in self.__props__}

    @classmethod
    def check_type(cls, key, val):
        if key not in cls.__props__:
            if cls._allowextra_:
                return
            raise ValueError(f"{key} is not valid for {cls._name_}")

        type_hint = cls.__props__[key]

        # We have to handle the 'special constructs' from the typing module differently
        # then the rest.
        if type_hint == typing.Any:
            # match everything
            return

        if type_hint == typing.ClassVar:
            raise ValueError(
                f"{key} is not valid for {cls._name_}, as a ClassVar this should only"
                "be set in code, not in settings."
            )

        # If the type has an __origin__ attribute, use that instead of itself
        # examples are typing.List[str].__origin__ = list
        # we are not going to actually try and verify the args... so List[str] we
        # do not go in and check every element to be a string
        base_type_hint = getattr(type_hint, "__origin__", None) or type_hint

        if base_type_hint in (typing.Union, typing.Optional):
            if type_hint.__args__ and not isinstance(val, type_hint.__args__):
                raise TypeError(
                    f"Unexpected type for {key} in element {cls._name_} "
                    f"expected one of {type_hint.__args__} but found {type(val)}"
                )
            return

        if not isinstance(val, base_type_hint):
            raise TypeError(
                f"Unexpected type for {key} in element {cls._name_} "
                f"expected {type_hint} but found {type(val)}"
            )
