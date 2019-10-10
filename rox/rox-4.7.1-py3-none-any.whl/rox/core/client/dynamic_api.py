from rox.core.entities.flag import Flag


class DynamicApi:
    def __init__(self, flag_repository, entities_provider):
        self.flag_repository = flag_repository
        self.entities_provider = entities_provider

    def is_enabled(self, name, default_value, context=None):
        variant = self.flag_repository.get_flag(name)
        if variant is None:
            variant = self.entities_provider.create_flag(default_value)
            self.flag_repository.add_flag(variant, name)

        if not isinstance(variant, Flag):
            return default_value

        is_enabled = variant._is_enabled(context, none_instead_of_default=True)
        return is_enabled if is_enabled is not None else default_value

    def value(self, name, default_value, options = [], context=None):
        variant = self.flag_repository.get_flag(name)
        if variant is None:
            variant = self.entities_provider.create_variant(default_value, options)
            self.flag_repository.add_flag(variant, name)

        value = variant._get_value(context, none_instead_of_default=True)
        return value if value is not None else default_value
