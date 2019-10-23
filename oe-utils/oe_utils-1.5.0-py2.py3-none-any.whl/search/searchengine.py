# -*- coding: utf-8 -*-
import json
import logging

import requests
from requests import HTTPError
from zope.interface import Interface
from zope.interface import implementer

from oe_utils.data.data_transfer_objects import ResultDTO

log = logging.getLogger(__name__)
NOT_SET = object()


class BulkException(Exception):
    pass


def load_searchquery_parameters(query_params, settings, user_acls=None):
    """
    Create a query for the searchengine based on the provided params.

    :param query_params: the request params for the search action
    :param settings: settings dictionary
    :param user_acls: an acces list for role based filtering
    :returns: Een :class:`dict` query object for the searchengine
    """
    q = {"match_all": {}}
    return q


def default_mapper(result, settings):
    if "hits" in result:
        result = [r["_source"] for r in result["hits"]["hits"]]
        return result
    else:
        return []


class ISearchEngine(Interface):
    def bulk_add_to_index(
        self, system_token, object_type, data, id_field="id", batch_size=5000
    ):
        """Add an iterable of data to the elasticsearch index in bulk."""

    def add_to_index(system_token, object_type, object_id, object_data):
        """Add an object to the index with a specific type."""

    def remove_from_index(system_token, object_type, object_id):
        """Remove an object from the index."""

    def remove_from_index_by_query(system_token, object_field, object_value):
        """Remove an object from the index by query."""

    def query(
        system_token,
        object_type=None,
        query_params=None,
        sort=None,
        result_range=None,
        mapper=default_mapper,
        load_searchquery_param_func=load_searchquery_parameters,
        aggregations=None,
        settings=None,
        user_acls=None,
        min_score=None,
        principals=NOT_SET,
        source=None,
    ):
        """Execute a query on the search engine."""

    def remove_index(system_token):
        """Remove the index."""

    def create_index(system_token, data=None):
        """Create the index."""

    def add_type_mapping(object_type, object_type_mapping, system_token):
        """Add the mapping for specific type."""


@implementer(ISearchEngine)
class SearchEngine(object):
    def __init__(self, baseurl, index_name, version="1"):
        self.baseurl = baseurl
        self.index_name = index_name
        self.version = version
        self.content_header = (
            {"Content-Type": "application/json"} if self.version == "6" else {}
        )

    def assert_response_ok(self, response):
        try:
            response.raise_for_status()
        except HTTPError:
            log.error(response.text)
            raise

    def add_to_index(self, system_token, object_type, object_id, object_data):
        """Add an object to the index with a specific type."""
        if object_type and object_type != "_doc":
            log.info(
                "The use of object types is discouraged by Elasticsearch "
                "and will be depecreated in future versions: "
                "https://www.elastic.co/guide/en/elasticsearch/reference/current/removal-of-types.html "  # noqa
            )
        headers = {"OpenAmSSOID": system_token} if system_token else {}
        headers.update(self.content_header)
        res = requests.put(
            self.baseurl
            + "/"
            + self.index_name
            + "/"
            + object_type
            + "/"
            + str(object_id),
            object_data,
            headers=headers,
        )
        self.assert_response_ok(res)

    def bulk_add_to_index(
        self, system_token, object_type, data, id_field="id", batch_size=5000
    ):
        """
        Add an iterable of data to the elasticsearch index in bulk.

        The _id being set at elasticsearch is taken from the "id_field" in
        each json dict. If the key is not found, no _id will be set and
        Elasticsearch will generate one.

        :param system_token: OpenAmSSOID header for request to Elasticsearch
        :param object_type: The type to add the index to.
        :param data: An iterable of json dicts to add to the index.
        :param id_field: The field in the data which should become the _id in
                         Elasticsearch
        :param batch_size: Maximum amount of items to send per batch.
        :return:
        """
        bulk_url = self.baseurl + "/" + self.index_name + "/" + object_type + "/_bulk"
        batch_data = ""
        for i, item in enumerate(data, start=1):
            action = {"index": {}}
            if id_field in item:
                action["index"]["_id"] = item[id_field]
            batch_data += json.dumps(action) + "\n" + json.dumps(item) + "\n"
            if i % batch_size == 0:
                self._send_batch(system_token, bulk_url, batch_data)
                batch_data = ""
        if batch_data:
            self._send_batch(system_token, bulk_url, batch_data)

    def _send_batch(self, system_token, bulk_url, batch_data):
        headers = {"OpenAmSSOID": system_token} if system_token else {}
        if self.version not in ("1", "2", "3", "4"):
            headers["Content-Type"] = "application/x-ndjson"
        res = requests.put(bulk_url, data=batch_data, headers=headers)
        self.assert_response_ok(res)
        if res.json().get("errors"):
            raise BulkException(
                "Result from bulk operation contains errors: " + res.text
            )

    def remove_from_index(self, system_token, object_type, object_id):
        """Remove an object from the index."""
        headers = {"OpenAmSSOID": system_token} if system_token else {}
        res = requests.delete(
            self.baseurl
            + "/"
            + self.index_name
            + "/"
            + object_type
            + "/"
            + str(object_id),
            headers=headers,
        )
        self.assert_response_ok(res)

    def remove_from_index_by_query(self, system_token, object_field, object_value):
        """Remove an object from the index by query."""
        headers = {"OpenAmSSOID": system_token} if system_token else {}
        if self.version == "1":
            res = requests.delete(
                self.baseurl
                + "/"
                + self.index_name
                + "/_query?q="
                + object_field
                + ":"
                + str(object_value),
                headers=headers,
            )
        else:
            headers.update(self.content_header)
            delete_query = {"query": {"match": {object_field: object_value}}}
            res = requests.post(
                self.baseurl + "/" + self.index_name + "/_delete_by_query",
                data=json.dumps(delete_query),
                headers=headers,
            )
        self.assert_response_ok(res)

    def build_query(
        self,
        query_params=None,
        sort=None,
        result_range=None,
        load_searchquery_param_func=load_searchquery_parameters,
        aggregations=None,
        settings=None,
        user_acls=None,
        min_score=None,
        source=None,
    ):
        """
        Build the elastic search query and the result range params.

        :param self:
        :param query_params: query params passed to load_searchquery_param_func
           and source if callable.
        :param sort: sort value of the query.
        :param result_range: oe_utils Range object to set `from` and `size`
           parameters on the query.
        :param load_searchquery_param_func: callable which takes query_params,
           settings and user_acls=user_acls as parameter. This callable's
           return value will be put in the "query" key of the query.
        :param aggregations: aggregations dict, put directly into the
           "aggregations" key of the query
        :param settings: settings passed to load_searchquery_param_func,
           source if callable and mapper
        :param user_acls: passed to the load_searchquery_param_func and source
           if callable.
        :param min_score: min_score value of the query
        :param source: If callable, acts like load_searchquery_param_func and
           this will be called during the query exection with parameters:
           query_params, settings, user_acls=user_acls.
           The return value will be set as "_source" in the query.
           If not callable this is put directly into the "_source" of the query
        :return: dict that contains the full query and the result range params
        """
        query = load_searchquery_param_func(query_params, settings, user_acls=user_acls)
        if not sort:
            sort = ["_score"]
        params = {}
        if result_range:
            params["size"] = result_range.get_page_size()
            params["from"] = result_range.start
        data = {"query": query, "sort": sort}
        if min_score:
            data["min_score"] = min_score
        if aggregations:
            data["aggregations"] = aggregations
        if source is not None:
            try:
                source = source(query_params, settings, user_acls=user_acls)
            except TypeError:
                pass
            data["_source"] = source

        return {"es_query": data, "params": params}

    def run_query(
        self,
        system_token,
        es_query,
        params,
        object_type=None,
        mapper=default_mapper,
        settings=None,
        principals=NOT_SET,
    ):
        """
        Execute a query on the search engine.

        :param system_token: system token.
        :param es_query: the full elastic search query
        :param params: request paramteres containing the result range
        :param object_type: type in index. When passed, the query will be
           executed to <es>/index/object_type/_search, when None, the query is
           send to <es>/index/_search
        :param mapper: callable used to process the response into data. It will
           receive the ES result, the settings and, if provided, principals as
           parameters. The return result will be put in the `.data` property
           of the response.
        :param settings: settings passed to load_searchquery_param_func,
           source if callable and mapper
        :param principals: this is a parameter given to the mapper function if
           it is not None, otherwise this is not passed.
        :return: ResultDTO with data, total, and aggregations.
        """
        headers = {"OpenAmSSOID": system_token} if system_token else {}
        headers.update(self.content_header)
        search_url = self.baseurl + "/" + self.index_name
        # if no object_type assume full index search
        search_url += "/" + object_type + "/_search" if object_type else "/_search"
        res = requests.post(
            search_url, data=json.dumps(es_query), params=params, headers=headers
        )
        self.assert_response_ok(res)
        result = json.loads(res.text)
        mapper_args = [result, settings]
        if principals != NOT_SET:
            mapper_args.append(principals)
        return ResultDTO(
            mapper(*mapper_args),
            result["hits"]["total"] if "hits" in result else 0,
            result["aggregations"] if "aggregations" in result else None,
        )

    def query(
        self,
        system_token,
        object_type=None,
        query_params=None,
        sort=None,
        result_range=None,
        mapper=default_mapper,
        load_searchquery_param_func=load_searchquery_parameters,
        aggregations=None,
        settings=None,
        user_acls=None,
        min_score=None,
        principals=NOT_SET,
        source=None,
    ):
        """
        Execute a query on the search engine.

        :param system_token: system token.
        :param object_type: type in index. When passed, the query will be
           executed to <es>/index/object_type/_search, when None, the query is
           send to <es>/index/_search
        :param query_params: query params passed to load_searchquery_param_func
           and source if callable.
        :param sort: sort value of the query.
        :param result_range: oe_utils Range object to set `from` and `size`
           parameters on the query.
        :param mapper: callable used to process the response into data. It will
           receive the ES result, the settings and, if provided, principals as
           parameters. The return result will be put in the `.data` property
           of the response.
        :param load_searchquery_param_func: callable which takes query_params,
           settings and user_acls=user_acls as parameter. This callable's
           return value will be put in the "query" key of the query.
        :param aggregations: aggregations dict, put directly into the
           "aggregations" key of the query
        :param settings: settings passed to load_searchquery_param_func,
           source if callable and mapper
        :param user_acls: passed to the load_searchquery_param_func and source
           if callable.
        :param min_score: min_score value of the query
        :param principals: this is a parameter given to the mapper function if
           it is not None, otherwise this is not passed.
        :param source: If callable, acts like load_searchquery_param_func and
           this will be called during the query exection with parameters:
           query_params, settings, user_acls=user_acls.
           The return value will be set as "_source" in the query.
           If not callable this is put directly into the "_source" of the query
        :return: ResultDTO with data, total, and aggregations.
        """
        query_build = self.build_query(
            query_params=query_params,
            sort=sort,
            result_range=result_range,
            load_searchquery_param_func=load_searchquery_param_func,
            aggregations=aggregations,
            settings=settings,
            user_acls=user_acls,
            min_score=min_score,
            source=source,
        )
        return self.run_query(
            system_token,
            es_query=query_build["es_query"],
            params=query_build["params"],
            object_type=object_type,
            mapper=mapper,
            settings=settings,
            principals=principals,
        )

    def remove_index(self, system_token):
        headers = {"OpenAmSSOID": system_token} if system_token else {}
        res = requests.head(self.baseurl + "/" + self.index_name, headers=headers)
        if res.status_code < 400:  # otherwise assume index doens't exists
            res = requests.delete(self.baseurl + "/" + self.index_name, headers=headers)
            self.assert_response_ok(res)

    def create_index(self, system_token, data):
        headers = {"OpenAmSSOID": system_token} if system_token else {}
        headers.update(self.content_header)
        res = requests.put(
            self.baseurl + "/" + self.index_name, data=json.dumps(data), headers=headers
        )
        self.assert_response_ok(res)

    def add_type_mapping(self, object_type, object_type_mapping, system_token):
        headers = {"OpenAmSSOID": system_token} if system_token else {}
        headers.update(self.content_header)
        res = requests.put(
            self.baseurl + "/" + self.index_name + "/_mapping/" + object_type,
            data=json.dumps(object_type_mapping),
            headers=headers,
        )
        self.assert_response_ok(res)
