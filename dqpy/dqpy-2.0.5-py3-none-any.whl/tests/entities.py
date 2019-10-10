from schematics.types import StringType

from dq.entity import Entity


class SimpleEntity(Entity):

    name = StringType()
