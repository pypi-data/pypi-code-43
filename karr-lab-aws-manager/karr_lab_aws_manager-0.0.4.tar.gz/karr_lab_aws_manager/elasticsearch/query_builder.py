from karr_lab_aws_manager.elasticsearch import util
import requests


class QueryBuilder(util.EsUtil):

    def __init__(self, profile_name=None, credential_path=None,
                config_path=None, elastic_path=None,
                cache_dir=None, service_name='es', max_entries=float('inf'), verbose=False):
        ''' 
            Args:
                profile_name (:obj: `str`): AWS profile to use for authentication
                credential_path (:obj: `str`): directory for aws credentials file
                config_path (:obj: `str`): directory for aws config file
                elastic_path (:obj: `str`): directory for file containing aws elasticsearch service variables
                cache_dir (:obj: `str`): temp directory to store json for bulk upload
                service_name (:obj: `str`): aws service to be used
                max_entries (:obj: `int`): maximum number of operations
                verbose (:obj: `bool`): verbose messages
        '''
        super().__init__(profile_name=profile_name, credential_path=credential_path,
                config_path=config_path, elastic_path=elastic_path,
                cache_dir=cache_dir, service_name=service_name, max_entries=max_entries, verbose=verbose)


    def _set_options(self, query, option_key, option_value):
        ''' Builds query options for elasticsearch
            (https://opendistro.github.io/for-elasticsearch-docs/docs/elasticsearch/full-text/#options)
            Args:
                query_operation (:obj: `dict`): query body
                option_key (:obj: `str`): option name
                option_value (:obj: `str`) option value
            Returns:
                query (:obj: `dict`): new query body
        '''
        query_operation = list(query['query'].keys())[0]
        query['query'][query_operation][option_key] = option_value
        return query
    
    def build_simple_query_string_body(self, query_message, **kwargs):
        ''' Builds query portion of the body in request body search
            (https://opendistro.github.io/for-elasticsearch-docs/docs/elasticsearch/full-text/#simple-query-string)
            Args:
                query_message (:obj: `str`): string to be queried for.
            Returns:
                query (:obj: `dict`): request body
        '''
        query_operation = 'simple_query_string'
        query = {'query': {query_operation: {'query': query_message }}}

        fields = kwargs.get('fields')
        query = self._set_options(query, 'fields', fields)

        flags = kwargs.get('flags', 'ALL')
        query = self._set_options(query, 'flags', flags)

        fuzzy_transpositions = kwargs.get('fuzzy_transpositions', True)
        query = self._set_options(query, 'fuzzy_transpositions', fuzzy_transpositions)

        fuzzy_max_expansions = kwargs.get('fuzzy_max_expansions', 50)
        query = self._set_options(query, 'fuzzy_max_expansions', fuzzy_max_expansions)

        fuzzy_prefix_length = kwargs.get('fuzzy_prefix_length', 0)
        query = self._set_options(query, 'fuzzy_prefix_length', fuzzy_prefix_length)

        minimum_should_match = kwargs.get('minimum_should_match', 1)
        query = self._set_options(query, 'minimum_should_match', minimum_should_match)

        analyze_wildcard = kwargs.get('analyze_wildcard', False)
        query = self._set_options(query, 'analyze_wildcard', analyze_wildcard)

        lenient = kwargs.get('lenient', False)
        query = self._set_options(query, 'lenient', lenient)

        quote_field_suffix = kwargs.get('quote_field_suffix', "")
        query = self._set_options(query, 'quote_field_suffix', quote_field_suffix)

        auto_generate_synonyms_phrase_query = kwargs.get('auto_generate_synonyms_phrase_query', True)
        query = self._set_options(query, 'auto_generate_synonyms_phrase_query', auto_generate_synonyms_phrase_query)

        default_operator = kwargs.get('default_operator', 'or')
        query = self._set_options(query, 'default_operator', default_operator)

        analyzer = kwargs.get('analyzer', 'standard')
        query = self._set_options(query, 'analyzer', analyzer)
        
        return query

