class Posterizer:
  def __init__(self, index):
    self.index = index
    self.mapping = index.mapping
    
    self.posters = {
      'keyword': self.keyword_poster,
      'text': self.text_poster,
      'float': self.float_poster,
      'integer': self.integer_poster,
      'boolean': self.boolean_poster,
      'scored_keyword': self.scored_keyword_poster,
#     'object': self.object_poster
    }
  
  def keyword_poster(self, field, doc_field_value):
    posts = []
    if doc_field_value is not None:
      if type(doc_field_value) is list:
        for v in doc_field_value:
          posts.extend(self.keyword_poster(field, v))
      else:
        row_key = self.index.get_row_key(field, doc_field_value)
        metadata = {'t': 't'}
        posts.append((row_key, metadata))
    return posts
  
  def text_poster(self, field, doc_field_value):
    field_spec = self.mapping.get_field_spec(field)
    posts = []
    token_to_count = {}
    value = doc_field_value
    if value:
      if type(doc_field_value) is list:
        value = ' '.join(doc_field_value)
      
      tokens = self.index.analyze(field, value)
      for token in tokens:
        token_to_count[token] = token_to_count.get(token, 0) + 1
      for token in token_to_count:
        row_key = self.index.get_row_key(field, token)
        metadata = {'t': 't'}
        if field_spec.get('fancy', False):
          metadata['s'] = token_to_count[token]
        posts.append((row_key, metadata))
    return posts
  
  def float_poster(self, field, doc_field_value):
    row_key = self.index.get_row_key(field, None)
    metadata = {'t': 'f', 's': float(doc_field_value)}
    return [(row_key, metadata)]
  
  def integer_poster(self, field, doc_field_value):
    row_key = self.index.get_row_key(field, None)
    metadata = {'t': 'i', 's': int(doc_field_value)}
    return [(row_key, metadata)]
  
  def boolean_poster(self, field, doc_field_value):
    row_key = self.index.get_row_key(field, doc_field_value)
    metadata = {'t': 'b'}
    return [(row_key, metadata)]
  
  def scored_keyword_poster(self, field, doc_field_value):
    posts = []
    if type(doc_field_value) is list:
      for e in doc_field_value:
        posts.extend(self.scored_keyword_poster(field, e))
    else:
      keyword = doc_field_value.get('kw')
      score = float(doc_field_value.get('s', 0))
      row_key = self.index.get_row_key(field, keyword)
      metadata = {'t': 'f', 's': score}
      posts.append((row_key, metadata))
    return posts
  
  def get_field_posts_for_doc(self, field, doc):
    field_type = self.mapping.get_type(field)
    return self.posters[field_type](field, doc)
  
  def _get_posts_for_doc(self, doc):
    posts = []
    for field in self.mapping.mapping:
      if field in doc and doc[field] is not None:
        field_posts = self.get_field_posts_for_doc(field, doc[field])
        posts.extend(field_posts)
        
        field_spec = self.mapping.get_field_spec(field)
        if field_spec.get('properties') is not None:
          for prop in field_spec.get('properties'):
            posts.extend(self.get_field_posts_for_doc(f'{field}.{prop}', doc[field]))
    return posts
  
  def get_posts_for_doc(self, doc):
      '''
      Consumes a document. Outputs a list of posts, which look like:
      (row_key, {'t': 't'})
      '''
      return self._get_posts_for_doc(doc)
