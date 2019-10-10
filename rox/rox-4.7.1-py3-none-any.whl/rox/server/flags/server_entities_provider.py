from rox.server.flags.rox_flag import RoxFlag
from rox.server.flags.rox_variant import RoxVariant


class ServerEntitiesProvider:
    def create_flag(self, default_value):
        return RoxFlag(default_value)

    def create_variant(self, default_value, options):
        return RoxVariant(default_value, options)
