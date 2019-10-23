from  .query_components import Bool, Must, Should, Filter, MustNot, Boost, FieldBoost, \
                              Interleave, Match, NormalizedMatch, Range, ScoredTerm, Term, Terms

from .utils import QueryParserValidator

query_name_to_component = {
  'bool': Bool,
  'must': Must,
  'should': Should,
  'filter': Filter,
  'must_not': MustNot,
  'boost': Boost,
  'field_boost': FieldBoost,
  'interleave': Interleave,
  'match': Match,
  'normalized_match': NormalizedMatch,
  'range': Range,
  'scored_term': ScoredTerm,
  'term': Term,
  'terms': Terms
}


def parse_query(query, source='query'):
  ''' query (dict) => (QueryComponent) '''
  QueryParserValidator.is_single_value_dict(query, source=source)

  query_root = [k for k in query][0]

  QueryParserValidator.is_valid_op(query_root, query_name_to_component, source=source)

  root_body = query[query_root]

  return query_name_to_component[query_root].from_json(root_body, parse_query)
