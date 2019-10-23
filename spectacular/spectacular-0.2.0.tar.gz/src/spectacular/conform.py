from spectacular.validation import CustomValidator, validate
from spectacular.schemas import select, Context, allows_null


## IMPROVE: We might want to extend this with a function that maps object
## keys. This makes it easier the uniformize JSON conventions over different
## stacks.
class Conformer:
    def __init__(
        self, schema, context=Context.CREATE, ignored=None, validator=CustomValidator
    ):

        self._schema = schema
        self.context = context
        self.validator = validator
        if ignored is None:
            self.ignored = set([])
        else:
            self.ignored = set(ignored)
        self.__schema = None

    @property
    def schema(self):
        """Return the context-adapted schema."""
        if self.__schema is None:
            self.__schema = select(self._schema, self.context, self.ignored)
        return self.__schema

    def __call__(self, value):
        """Conforms the value in place."""
        if self._schema.get("type") == "object":
            validate(self.schema, value, self.validator)
            result = {}
            for (name, subschema) in self.schema["properties"].items():
                if name not in self.ignored:
                    if name in value:
                        result[name] = value[name]
                    elif self.context is Context.CREATE and allows_null(subschema):
                        result[name] = None

            return result
        validate(self._schema, value, self.validator)
        return value


def conform(schema, context=Context.CREATE, ignored=None):
    return Conformer(schema, context, ignored)
