import jsontrips

assert type(jsontrips.lexicon()) is dict
assert type(jsontrips.feature_lists()) is dict
assert type(jsontrips.feature_types()) is dict
assert type(jsontrips.lexicon_pos()) is dict
assert type(jsontrips.ontology()) is dict
assert type(jsontrips.syntax_templates()) is dict

assert type(jsontrips.lexicon()) is dict
assert type(jsontrips.feature_lists()) is dict
assert type(jsontrips.feature_types()) is dict
assert type(jsontrips.lexicon_pos()) is dict
assert type(jsontrips.ontology()) is dict
assert type(jsontrips.syntax_templates()) is dict

assert len(jsontrips.lexicon()) > 0
assert len(jsontrips.feature_lists()) > 0
assert len(jsontrips.feature_types()) > 0
assert len(jsontrips.lexicon_pos()) > 0
assert len(jsontrips.ontology()) > 0
assert len(jsontrips.syntax_templates()) > 0


