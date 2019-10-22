"""
TODO: The Entity library

"""

import json
from . import utils

SCHEMA_VERSION = 'http://json-schema.org/draft-07/schema#'


class Entity(object):

    def __init__(self, schema=None, type=None):
        self.schema = schema or dict()
        self.set_type(type)

    def set_type(self, type):
        self.schema['type'] = type

    def set_description(self, description):
        self.schema['description'] = description

    def json(self):
        """ Print a JSON representatoin of the Entity"""
        print(json.dumps(self.schema, sort_keys=True, indent=4))


class Object(Entity):
    """
    Pythonic representation of a Complex Object
    """

    def __init__(self, schema=None, uri=None, features_key = 'features'):
        # Set a custom features key
        self.features_key = features_key.replace(" ","_")
        if schema:
            super().__init__(schema=schema, type='object')
        else:
            super().__init__(type='object')
            s = self.schema
            s['$schema'] = SCHEMA_VERSION
            s['$id'] = uri
            s['allOf'] = list()
            object_properties = {
                "properties": {
                    self.features_key : {
                        "type": "object",
                        "allOf": [
                            {
                                "properties": {},
                                "required": []
                            }
                        ]
                    }
                }
            }
            s['allOf'].append(object_properties)


    def __repr__(self):
        return f"<Pythonic Object representation of {self.schema['$id']})>"


    def get_features(self):
        """
        Return objects features (local)
        """
        features = dict()
        for feature in self.schema['allOf'][0]['properties'][self.features_key]['allOf'][0]['properties']:
            features[feature] = self.schema['allOf'][0]['properties'][self.features_key]['allOf'][0]['properties'][feature]
        return features


    def get_features_paths(self, schema_store):
        """
        Return a list of schema paths (also if inherited)
        """
        dereferenced_schema = self.dereference(schema_store)
        return utils.explore_paths(dereferenced_schema)


    def set_feature(self, **kwargs):
        """
        Set a local feature
        """
        for key, value in kwargs.items():
            if type(value) == ObjectReference:
                new_data = value
            else:
                new_data = value.schema

            self.schema['allOf'][0]['properties'][self.features_key]['allOf'][0]['properties'][key] = new_data


    def remove_features(self, *args):
        """
        Remove a local feature
        """

        for f in args:
            try:
                del self.schema['allOf'][0]['properties'][self.features_key]['allOf'][0]['properties'][f]
                self.remove_required_features(f)
            except KeyError:
                pass
                #print(f'{f} is ignored since it is not a current feature of this object')

    def get_required_features(self):
        """
        Return a list of (locally) required properties
        """
        return self.schema['allOf'][0]['properties'][self.features_key]['allOf'][0]['required']

    def add_required_features(self, *args):
        """
        Add a (locally) required properties
        """

        required = self.schema['allOf'][0]['properties'][self.features_key]['allOf'][0]['required']

        for f in args:
            required.append(f)

        # remove duplicates and sort
        self.schema['allOf'][0]['properties'][self.features_key]['allOf'][0]['required'] = sorted(
            list(set(required)))

    def remove_required_features(self, *args):
        """
        Remove a (locally) required properties
        """

        required = self.schema['allOf'][0]['properties'][self.features_key]['allOf'][0]['required']

        if args:
            for f in args:
                try:
                    required.remove(f)
                except ValueError:
                    pass
                    # print(f'{f} is ignored since it is not a current feature of this object')

        # sort
        self.schema['allOf'][0]['properties'][self.features_key]['allOf'][0]['required'] = sorted(
            required)

    def dereference(self, schema_store):
        """
        dereference the object against a schema_store and return its schema representation
        """
        return schema_store.resolve(self.schema)

    def extend(self, *args):
        """
        Extend the current schema

        See https://github.com/json-schema-org/json-schema-spec/issues/348#issuecomment-322940347 for inheritance limitations
        """

        # Extension are stored in the list stored in the key allOf (from index 1 onwards)
        extensions = self.schema['allOf'][1:]

        for objRef in args:

            if type(objRef) != ObjectReference:
                raise Exception(
                    'function arguments must be an instance of jsondesign.entity.ObjectReference')

            extensions.append(objRef)

        # remove duplicates and update
        self.schema['allOf'] = [
            self.schema['allOf'][0]] + list(set(extensions))


class ObjectReference(dict):
    """ Just a reference to an object"""

    def __init__(self, uri, *args, **kwargs):
        super().__init__({'$ref': uri}, *args, **kwargs)

    def __hash__(self):
        return hash(self['$ref'])


class String(Entity):

    def __init__(self):
        super().__init__(type="string")

    def set_minLength(self, minLength):
        self.schema['minLength'] = int(minLength)

    def set_maxLength(self, maxLength):
        self.schema['maxLength'] = int(maxLength)

    def set_regex(self, pattern):
        self.schema['pattern'] = pattern

    def setFormat(self):
        pass


class Numeric(Entity):

    def __init__(self, numeric_type):
        if numeric_type in ['integer', 'number']:
            super().__init__(type=numeric_type)
        else:
            raise Exception('Numeric type must be integer or number')

    def set_multipleOf(self, multipleOf):
        self.schema['multipleOf'] = multipleOf

    def set_minimum(self, minimum, exclusive=True):
        if exclusive:  # X > k
            self.schema['exclusiveMinimum'] = minimum
        else:  # X >= k
            self.schema['minimum'] = minimum

    def set_maximum(self, maximum, exclusive=True):
        if exclusive:  # X > k
            self.schema['exclusiveMaximum'] = maximum
        else:  # X >= k
            self.schema['maximum'] = maximum


class Array(Entity):

    def __init__(self):
        super().__init__(type="array")

    def set_ItemsType(self, item):
        if type(item) == ObjectReference:
            item_schema = item
        else:
            item_schema = item.schema

        self.schema['items'] = item_schema

    def set_minItems(self, minItems):
        self.schema['minItems'] = minItems

    def set_maxItems(self, maxItems):
        self.schema['maxItems'] = maxItems


class Boolean(Entity):

    def __init__(self):
        super().__init__(type="boolean")


class Null(Entity):

    def __init__(self):
        super().__init__(type="null")
