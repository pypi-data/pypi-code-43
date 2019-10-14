from .query_component import QueryComponent
from .must import Must
from .should import Should
from ._filter import Filter
from .must_not import MustNot
from ..low_level import sorted_in1d, combine_must_should
from ..query_result import IdsQR, IdsScoresQR
from ..utils import QueryParserValidator

class Bool(QueryComponent):
  op_name = 'bool'
  def __init__(self, must=None, should=None, _filter=None, must_not=None):
    super().__init__('Bool')
    self.must = must
    self.should = should
    self._filter = _filter
    self.must_not = must_not
  
  def validate(self, index, score=True):
    if self.must is None and self._filter is None and self.should is None:
      raise Exception('bool must specify at least one of [must, should, _filter]')
    
    if self.must is not None:
      if not isinstance(self.must, Must):
        raise Exception('bool.must is a non-Must')
      self.must.validate(index, score=True)

    if self.should is not None:
      if not isinstance(self.should, Should):
        raise Exception('bool.should is a non-Should')
      self.should.validate(index, score=True)

    if self._filter is not None:
      if not isinstance(self._filter, Filter):
        raise Exception('bool._filter is a non-Filter')
      self._filter.validate(index, score=False)

    if self.must_not is not None:
      if not isinstance(self.must_not, MustNot):
        raise Exception('bool.must_not is a non-MustNot')
      self.must_not.validate(index, score=False)

    return True
    

  def execute(self, index, score=True):
    has_filter = self._filter is not None
    has_must_not = self.must_not is not None
    has_must = self.must is not None
    has_should = self.should is not None

    has_any_filter = has_filter or has_must_not
    has_any_score = has_must or has_should

    has_filter_and_must_not = has_filter and has_must_not
    has_must_and_should = has_must and has_should

    if has_any_filter:
      combined_filter_ids = None
      combined_filter_invert = False
      if has_filter:
        _filter = self._filter.execute(index, score=False)
        if has_must_not:
          # if it has both, we can combine them to a single ids list
          _must_not = self.must_not.execute(index, score=False)

          # using sorted_in1d with invert=True returns the ids in the first arg that are not in the second
          combined_filter_ids = _filter.getIds()[sorted_in1d(_filter.getIds(), _must_not.getIds(), invert=True, assume_sorted=True)]
          combined_filter_invert = False
        else:
          combined_filter_ids = _filter.getIds()
          combined_filter_invert = False
      else:
        combined_filter_ids = self.must_not.execute(index, score=False).getIds()
        combined_filter_invert = True

      if has_must_and_should:
        _should = self.should.execute(index, score=True)
        _must = self.must.execute(index, score=True)

        filtered_must_mask = sorted_in1d(_must.getIds(), combined_filter_ids, invert=combined_filter_invert)
        _filtered_must_qr = IdsScoresQR(_must.getIds()[filtered_must_mask], _must.getScores()[filtered_must_mask])
        fm_s_ids, fm_s_scores = combine_must_should(_filtered_must_qr.getIds(), _filtered_must_qr.getScores(), _should.getIds(), _should.getScores(), assume_sorted=True)
        return IdsScoresQR(fm_s_ids, fm_s_scores)
      elif has_must:
        _must = self.must.execute(index, score=True)

        filtered_must_mask = sorted_in1d(_must.getIds(), combined_filter_ids, invert=combined_filter_invert, assume_sorted=True)
        _filtered_must_qr = IdsScoresQR(_must.getIds()[filtered_must_mask], _must.getScores()[filtered_must_mask])
        return _filtered_must_qr
      elif has_should:
        _should = self.should.execute(index, score=True)

        filtered_should_mask = sorted_in1d(_should.getIds(), combined_filter_ids, invert=combined_filter_invert, assume_sorted=True)
        _filtered_should_qr = IdsScoresQR(_should.getIds()[filtered_should_mask], _should.getScores()[filtered_should_mask])
        return _filtered_should_qr
      else:
        return IdsQR(combined_filter_ids)  
    else:
      # there are not filter / must_not
      # if there is must and should we combine, otherwise, return the one present
      if has_must_and_should:
        # combine must and should
        _should = self.should.execute(index, score=True)
        _must = self.must.execute(index, score=True)
        fm_s_ids, fm_s_scores = combine_must_should(_must.getIds(), _must.getScores(), _should.getIds(), _should.getScores(), assume_sorted=True)
        return IdsScoresQR(fm_s_ids, fm_s_scores)
      elif has_must:
        _must = self.must.execute(index, score=True)
        return _must
      else:
        _should = self.should.execute(index, score=True)
        return _should
  
  def required_rows(self, index, score=True):
    req_rows = set()

    if self.must is not None:
      rr = self.must.required_rows(index, score=score)
      req_rows = req_rows.union(rr)
    
    if self.should is not None:
      rr = self.should.required_rows(index, score=score)
      req_rows = req_rows.union(rr)
    
    if self._filter is not None:
      rr = self._filter.required_rows(index, score=score)
      req_rows = req_rows.union(rr)
    
    if self.must_not is not None:
      rr = self.must_not.required_rows(index, score=score)
      req_rows = req_rows.union(rr)

    return req_rows

  def from_json(query, parse_query_fn):
    QueryParserValidator.is_dict(query, source='bool')
    QueryParserValidator.is_not_empty(query, source='bool')
    valid_ops = {'must', 'should', 'must_not', 'filter'}
    for key in query:
      QueryParserValidator.is_valid_op(key, valid_ops, source='bool')

    _must = query.get('must')
    _should = query.get('should')
    _filter = query.get('filter')
    _must_not = query.get('must_not')

    if _must is not None:
      _must = parse_query_fn({'must': _must})
    if _should is not None:
      _should = parse_query_fn({'should': _should})
    if _filter is not None:
      _filter = parse_query_fn({'filter': _filter})
    if _must_not is not None:
      _must_not = parse_query_fn({'must_not': _must_not})

    return Bool(must=_must, should=_should, _filter=_filter, must_not=_must_not)