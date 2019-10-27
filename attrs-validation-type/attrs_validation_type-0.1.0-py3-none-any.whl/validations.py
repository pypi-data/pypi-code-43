import attr

__all__ = ['type_of']

@attr.s(repr=False, slots=True, hash=True)
class TypeValidator(object):
    type = attr.ib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not type(value) == self.type:
            raise TypeError(
                "'{name}' must be {type!r} (got {value!r} that is a "
                "{actual!r}).".format(
                    name=attr.name,
                    type=self.type,
                    actual=value.__class__,
                    value=value,
                ),
                attr,
                self.type,
                value,
            )

    def __repr__(self):
        return "<type validator for type {type!r}>".format(
            type=self.type
        )


def type_of(type):
    return TypeValidator(type)

