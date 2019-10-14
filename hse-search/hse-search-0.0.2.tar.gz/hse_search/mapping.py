class Mapping:
  def __init__(self, mapping):
    self.mapping = mapping
    self.fields_to_types = self.get_field_types_from_mapping(mapping)
    self.fields_to_analyzers = self.get_analyzers_from_mapping(mapping)
  
  def get_type(self, field):
    assert type(field) is str
    return self.fields_to_types.get(field)
  
  def get_analyzer(self, field):
    assert type(field) is str
    return self.fields_to_analyzers.get(field)
  
  def get_field_types_from_mapping(self, mapping):
    ftt = {}
    for field_name in mapping:
      ftype = mapping[field_name].get('type')
      properties = mapping[field_name].get('properties')
      if ftype is not None:
        ftt[field_name] = ftype
      if properties is not None:
        sub_fields = self.get_field_types_from_mapping(properties)
        for sf in sub_fields:
          ftt['%s.%s' % (field_name, sf)] = sub_fields[sf]
    return ftt

  def get_analyzers_from_mapping(self, mapping):
    fta = {}
    for field_name in mapping:
      ftype = mapping[field_name].get('type')
      analyzer_type = mapping[field_name].get('analyzer', 'english')
      properties = mapping[field_name].get('properties')
      if ftype == 'text':
        fta[field_name] = analyzer_type
      if properties is not None:
        sub_fields = self.get_analyzers_from_mapping(properties)
        for sf in sub_fields:
          fta['%s.%s' % (field_name, sf)] = sub_fields[sf]
    return fta