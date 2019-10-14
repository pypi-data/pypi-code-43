import base64

from google.cloud import storage

def get_blob_string_from_bucket(bucket, blob_name):
  blob = bucket.blob(blob_name)
  return blob.download_as_string().decode('utf-8')

def set_blob_string_from_bucket(bucket, blob_name, content):
  blob = bucket.blob(blob_name)
  blob.upload_from_string(content)
  return True

def get_type_of_field_from_mapping(field, mapping):
    assert type(field) is str
    field_type = None
    spec = {}
    spec.update(mapping)
    for f in field.split('.'):
        spec = spec.get('properties', spec)
        spec = spec.get(f, {})
    field_type = spec.get('type')
    return field_type

def keyword_row_key_formatter(field, value):
    encoded_value = base64.b64encode(value.encode()).decode('utf-8')
    row_key = '%s|%s' % (field, encoded_value)
    return row_key

def integer_row_key_formatter(field, value):
    return field

def float_row_key_formatter(field, value):
    return field

def boolean_row_key_formatter(field, value):
    if type(value) is str:
        return '%s|%s' % (field, value)
    else:
        return '%s|%s' % (field, 'true' if value else 'false')

def doc_row_key_formatter(doc_id, _):
    return 'doc|%s' % (doc_id)

row_key_formatters = {
    'keyword': keyword_row_key_formatter,
    'text': keyword_row_key_formatter,
    'integer': integer_row_key_formatter,
    'float': float_row_key_formatter,
    'boolean': boolean_row_key_formatter,
    'scored_keyword': keyword_row_key_formatter,
    'doc': doc_row_key_formatter
}

class Validator:
  validation_type = ''

  @classmethod
  def is_single_value_dict(cls, value, source=''):
    if type(value) is not dict:
      raise Exception('%s[%s] Error: must be dict' % (cls.validation_type, source))

    if len(value) != 1:
      raise Exception('%s[%s] Error: dict must have a single root.' % (cls.validation_type, source))
  
  @classmethod
  def is_dict(cls, value, source=''):
    if type(value) is not dict:
      raise Exception('%s[%s] Error: value must be dict' % (cls.validation_type, source))
  
  @classmethod
  def is_str(cls, value, source=''):
    if type(value) is not str:
      raise Exception('%s[%s] Error: value must be str' % (cls.validation_type, source))
  
  @classmethod
  def is_number(cls, value, source=''):
    if type(value) is not int and type(value) is not float:
      raise Exception('%s[%s] Error: value must be a number' % (cls.validation_type, source))
  
  @classmethod
  def is_list(cls, value, source=''):
    if type(value) is not list:
      raise Exception('%s[%s] Error: value must be list' % (cls.validation_type, source))
  
  @classmethod
  def is_type(cls, value, _type, type_name, source=''):
    if type(value) is not _type:
      raise Exception('%s[%s] Error: value must be %s' % (cls.validation_type, source, type_name))
  
  @classmethod
  def is_instance(cls, value, _type, type_name, source=''):
    if not isinstance(value, _type):
      raise Exception('%s[%s] Error: value must be instance of %s' % (cls.validation_type, source, type_name))
  
  @classmethod
  def is_not_empty(cls, value, source=''):
    if len(value) == 0:
      raise Exception('%s[%s] Error: value must be non-empty' % (cls.validation_type, source))
  
  @classmethod
  def is_not_none(cls, value, source=''):
    if value is None:
      raise Exception('%s[%s] Error: value is None' % (cls.validation_type, source))

  @classmethod
  def is_nonempty_list(cls, value, source=''):
    if type(value) is not list:
      raise Exception('%s[%s] Error: value must be list' % (cls.validation_type, source))
    if len(value) == 0:
      raise Exception('%s[%s] Error: value must be non-empty list' % (cls.validation_type, source))
  
  @classmethod
  def is_list_of_str(cls, value, source=''):
    cls.is_list(value, source=source)

    for v in value:
      cls.is_str(v, source=source + '[:]')
    

class QueryParserValidator(Validator):
  validation_type = 'QueryParser'

  @classmethod
  def is_valid_op(cls, value, valid_ops, source=''):
    if value not in valid_ops:
      raise Exception('%s[%s] Error: unknown query operation (%s)' % (cls.validation_type, source, value))
    
class QueryValidatorValidator(Validator):
  validation_type = 'QueryValidator'

  @classmethod
  def is_valid_type(cls, value, valid_types, source=''):
    if value not in valid_types:
      raise Exception('%s[%s] Error: invalid type (%s)' % (cls.validation_type, source, value))
