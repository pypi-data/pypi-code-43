from rox.core.roxx.token_type import TokenTypes


class PropertiesExtensions:
    def __init__(self, parser, properties_repository):
        self.parser = parser
        self.properties_repository = properties_repository

    def extend(self):
        self.parser.add_operator('property', lambda parser, stack, context: property(self.properties_repository, parser, stack, context))


def property(properties_repository, parser, stack, context):
    prop_name = str(stack.pop())
    property = properties_repository.get_custom_property(prop_name)

    if property is None:
        stack.push(TokenTypes.UNDEFINED)
        return

    value = property.value(context)
    stack.push(TokenTypes.UNDEFINED if value is None else value)

