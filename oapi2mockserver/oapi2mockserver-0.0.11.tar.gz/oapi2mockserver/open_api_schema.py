import json
from jsonschema import validate


class OpenAPISchema(object):

    def get_example_json(self, schema):
        example = json.dumps(self.__parse({'schema': json.loads(schema)})['schema'])
        self.validate_json(schema, example)
        return example

    def validate_json(self, schema, json_data):
        validate(json.loads(json_data), json.loads(schema))
        return True

    def __parse(self, data):
        examples = {}
        for object_name, object_data in data.items():
            if 'example' not in object_data and 'items' not in object_data and 'properties' not in object_data:
                raise ExampleNotFoundException(object_name, 'No example found!')

            for key, value in object_data.items():
                if key == 'properties':
                    examples[object_name] = self.__parse(value)
                elif key == 'items':
                    examples[object_name] = [self.__parse({'items': value})['items']]
                elif key == 'example':
                    examples[object_name] = object_data[key]

        return examples


class ExampleNotFoundException(Exception):

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
