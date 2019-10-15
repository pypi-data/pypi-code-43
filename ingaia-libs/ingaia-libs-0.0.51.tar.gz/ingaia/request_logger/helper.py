import re
import json


def convert_dict_value_to_str(value):
    return json.dumps(value) if type(value) is dict else str(value)


def convert_values_to_str(doc, keys: list):
    for key in keys:
        if key in doc:
            doc[key] = convert_dict_value_to_str(doc[key])
    return doc


def normalize_dict_keys(doc):
    """
    Prevent the error:
    google.api_core.exceptions.BadRequest: 400 POST https://www.googleapis.com/bigquery/v2/projects/[...] :
    Invalid field name "[incorrect-field-name]". Fields must contain only letters, numbers, and underscores,
    start with a letter or underscore, and be at most 128 characters long.
    :param doc:
    :return:
    """
    new_doc = {}
    for key in doc.keys():
        # key - replace invalid characters for underscore
        k = re.sub(r'[\W_]+', '_', str(key).strip())

        # key - verify the beginning and the length
        if not re.match(r'[a-z_]', k[:1].lower()) or len(k) > 128:
            raise JsonInvalidFieldNameException()

        # value
        v = doc[key] if type(doc[key]) is not dict else normalize_dict_keys(doc[key])

        new_doc[k] = v

    return new_doc


class JsonInvalidFieldNameException(Exception):
    message = 'Fields must contain only letters, numbers, and underscores, start with ' \
              'a letter or underscore, and be at most 128 characters long.'

    def __init__(self):
        super(JsonInvalidFieldNameException, self).__init__(self.message)
