from rox.core.entities.variant import Variant


class Flag(Variant):
    FLAG_TRUE_VALUE = 'true'
    FLAG_FALSE_VALUE = 'false'

    def __init__(self, default_value=False):
        super(Flag, self).__init__(Flag.FLAG_TRUE_VALUE if default_value else Flag.FLAG_FALSE_VALUE, [Flag.FLAG_FALSE_VALUE, Flag.FLAG_TRUE_VALUE])

    def is_enabled(self, context):
        value = self.get_value(context=context)
        return self.is_enabled_from_string(value)

    def _is_enabled(self, context, none_instead_of_default):
        value = self._get_value(context, none_instead_of_default)
        return None if none_instead_of_default and value is None else self.is_enabled_from_string(value)

    def enabled(self, context, action):
        if self.is_enabled(context):
            action()

    def disabled(self, context, action):
        if not self.is_enabled(context):
            action()

    def is_enabled_from_string(self, value):
        return value == Flag.FLAG_TRUE_VALUE

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, True if self.default_value == Flag.FLAG_TRUE_VALUE else False)

    def __str__(self):
        return "%s(%s, name=%s, condition=%s)" % (type(self).__name__, True if self.default_value == Flag.FLAG_TRUE_VALUE else False, self.name, self.condition)
