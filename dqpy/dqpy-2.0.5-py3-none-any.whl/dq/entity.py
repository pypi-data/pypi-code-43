from schematics.models import Model


class Entity(Model):
    """Base entity class that provides shared utilities.

    Currently it only allows printing a schematics entity. More utilities
    may be added in the future. In any case, all entities should inherit from
    this class.
    """

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.to_primitive())
