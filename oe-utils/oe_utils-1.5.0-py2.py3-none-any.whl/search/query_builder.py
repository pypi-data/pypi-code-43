import re

# Each regex matches with 2 groups: 1) text to split  2) what to split on
# The regex for [Gent,groen] will result in:
# group1 = 'Gent,groen' and group2= ','
# The regex for Gent & groen will result in:
# group1 = 'Gent & groen' and group2= '&'
from deprecated import deprecated

AND_FILTER_REGEXES = [re.compile("([^&]+(&)(?:[^&]+&?)*)")]  # Matches Gent & groen
OR_FILTER_REGEXES = [re.compile(r"\[((?:[^,]+(,)?)+)\]")]  # Matches [Gent,groen]


class QueryBuilder(object):
    def __init__(self, query_params=None, es_version="1"):
        """
        Create a query builder.

        :param query_params: dict with query parameters
        """
        self.es_version = es_version
        self.query_params = query_params
        self.query = self._build_initial_query_string()
        self.filters = []

    def _build_initial_query_string(self):
        if (
            self.query_params is None
            or "query" not in self.query_params
            or self.query_params["query"] == ""
        ):
            return {"match_all": {}}
        else:
            all_fields = "_all" if self.es_version == "1" else "*"
            return {
                "query_string": {
                    "default_field": all_fields,
                    "query": self.query_params["query"],
                }
            }

    @deprecated(version="1.5.0", reason="Integrated in add_query_param_filters()")
    def add_named_concept_filters(self, named_filter_concepts):
        """
        Add named concept filters.

        :param named_filter_concepts: dict with named filter concepts which will be
        mapped as the key as query param and the value as search string
        """
        for concept_key, concept_name in named_filter_concepts.items():
            self.add_concept_filter(concept_key, concept_name=concept_name)

    def add_query_param_filters(self, query_param_names, query_param_translations=None):
        """
        Add query param filters.

        :param query_param_names: list with filter concepts
        :param query_param_translations: translates query_param to es_field
        """
        for query_param in query_param_names:
            if query_param_translations:
                es_field = query_param_translations.get(query_param)
            else:
                es_field = None
            self.add_query_param_filter(query_param, es_field=es_field)

    @deprecated(
        version="1.5.0", reason="Use function add_query_param_filters() instead"
    )
    def add_concept_filters(self, filter_concepts):
        """
        Add concept filters.

        :param filter_concepts: list with filter concepts
        """
        for concept in filter_concepts:
            self.add_concept_filter(concept)

    def add_query_param_filter(self, query_param_name, es_field=None):
        """
        Add a query_param filter.

        :param query_param_name: concept which will be used as
        lowercase string in a search term
        :param es_field: name of the place where there will be searched for
        """
        if query_param_name in self.query_params.keys():
            if not es_field:
                es_field = query_param_name
            if isinstance(self.query_params[query_param_name], list):
                es_filter = {"bool": {"should": []}}
                for or_filter in self.query_params[query_param_name]:
                    es_filter["bool"]["should"].append(
                        self._build_concept_term(es_field, or_filter)
                    )
            else:
                es_filter = self._build_concept_term(
                    es_field, self.query_params[query_param_name]
                )
            self.filters.append(es_filter)

    @deprecated(version="1.5.0", reason="Use function add_query_param_filter() instead")
    def add_concept_filter(self, concept, concept_name=None):
        """
        Add a concept filter.

        :param concept: concept which will be used as lowercase string in a search term
        :param concept_name: name of the place where there will be searched for
        """
        if concept in self.query_params.keys():
            if not concept_name:
                concept_name = concept
            if isinstance(self.query_params[concept], list):
                if self.es_version == "1":
                    es_filter = {"or": []}
                    for or_filter in self.query_params[concept]:
                        es_filter["or"].append(
                            self._build_concept_term(concept_name, or_filter)
                        )
                else:
                    es_filter = {"bool": {"should": []}}
                    for or_filter in self.query_params[concept]:
                        es_filter["bool"]["should"].append(
                            self._build_concept_term(concept_name, or_filter)
                        )
            else:
                es_filter = self._build_concept_term(
                    concept_name, self.query_params[concept]
                )
            self.filters.append(es_filter)

    def _build_query_param_term_filter(self, es_field, query_param_value):
        return {"term": {es_field: str(query_param_value).lower()}}

    def _build_concept_term(self, concept_name, concept):
        filter_method = "term" if str(self.es_version) == "1" else "match"
        return {filter_method: {concept_name: str(concept).lower()}}

    def parse_full_text_search_param(self, value):
        """
        Convert the user queryparam input to a valid query_string for ES.

        This does not really support quotes yet.

        Onroerend erfgoed has some custom rules as to how users can enter a
        query. For example, the user can use `&` to perform an "AND" query.
        This method will turn all the special cases from onroerend erfgoed
        into a valid query for Elasticsearch by, for example, turning "x & y"
        into "x + y".
        """
        result = self.parse_full_text_search_param_iterable(value)
        if result is not None:
            return result
        result = self.parse_full_text_search_param_or_patterns(value)
        if result is not None:
            return result
        result = self.parse_full_text_search_param_and_patterns(value)
        if result is not None:
            return result
        return value.strip()

    def parse_full_text_search_param_iterable(self, value):
        """
        Translate a list or tuple into AND for ES.

        Sending ?text=Gent&text=groen has to be seen as an AND.
        This method will transform the value ["Gent", "Groen"]
        into "(Gent) + (groen)".
        """
        if isinstance(value, list) or isinstance(value, tuple):
            filters = [self.parse_full_text_search_param(val) for val in value]
            return " + ".join("(" + parsed + ")" for parsed in filters)
        return None

    def parse_full_text_search_param_or_patterns(self, value):
        """
        Look for specific OR patterns and translate them to ES.

        Sending text=[Gent,groen] has to be seen as an OR.
        This method will transform the string "[Gent,groen]"
        into "Gent | groen"
        """
        for regex in OR_FILTER_REGEXES:
            match = regex.match(value)
            if match:
                values = match.group(1).split(match.group(2))
                filters = [self.parse_full_text_search_param(val) for val in values]
                return " | ".join(filters)
        return None

    def parse_full_text_search_param_and_patterns(self, value):
        """
        Look for specific AND patterns and translate them to ES.

        Sending text=Gent & groen has to be seen as an AND.
        This method will transform the string "Gent & Groen"
        into "Gent + groen"
        """
        for regex in AND_FILTER_REGEXES:
            match = regex.match(value)
            if match:
                values = match.group(1).split(match.group(2))
                filters = [self.parse_full_text_search_param(val) for val in values]
                return " + ".join(filters)
        return None

    def set_full_text_search_query(
        self,
        field_boosts,
        query,
        default_operator="AND",
        flags="AND|OR|NOT|PREFIX|PHRASE|PRECEDENCE|ESCAPE|WHITESPACE",
        analyze_wildcard=True,
    ):
        """
        Build a simple_query_string query.

        The fields will be taken from the `field_boosts` keys. And each field
        will receive a score boost from `field_boosts` values.
        This is not a filter but sets the query itself because we care about
        scores.

        :type field_boosts: dict[str, int]
        :param field_boosts: fields and their score boost values, 1 default.
        :type query: str
        :param query: the simple_query_string query.
        :type default_operator: str
        :param default_operator: default_operator of the simple_query_string.
           Set this to 'AND' or 'OR'
        :type flags: str
        :param flags: flags of the simple_query_string. By default this is
           all the flags except fuzzyness.
        :type analyze_wildcard: bool
        :param analyze_wildcard: analyze_wildcard of the simple_query_string.
           Setting this to true will allow prefix wildcard strings to work.
        """
        # analyze_wildcard true will make it so when a prefix wildcard is used,
        # the prefix is still analyzed. "pre-fix*" without analyze would make
        # ES look for the term "pre-fix". But by default the word would
        # (should) have been broken up into terms 'pre' and 'fix'. With
        # analyze true. ES will look for "pre" and "fix*".
        # ^x are the score boost numbers.
        fields = ["{}^{}".format(field, boost) for field, boost in field_boosts.items()]
        self.query = {
            "simple_query_string": {
                "fields": fields,
                "query": query,
                "default_operator": default_operator,
                "flags": flags,
                "analyze_wildcard": analyze_wildcard,
            }
        }

    def build(self):
        """
        Build the query string, which can be used for a search query.

        :return: the query string
        """
        if self.es_version == "1":
            if len(self.filters) > 0:
                return {
                    "filtered": {"query": self.query, "filter": {"and": self.filters}}
                }
            else:
                return self.query
        else:
            query = {"bool": {"must": self.query}}
            if len(self.filters) > 0:
                query["bool"]["filter"] = self.filters
            return query

    def and_(self, *filters):
        return {"bool": {"must": filters}}

    def or_(self, *filters):
        return {"bool": {"should": filters}}

    def not_(self, *filters):
        return {"bool": {"must_not": filters}}

    def field_exists(self, field_name):
        return {"exists": {"field": field_name}}
