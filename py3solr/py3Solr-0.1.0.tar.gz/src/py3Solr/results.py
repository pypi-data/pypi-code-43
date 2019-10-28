#!win10_x64 python3.6
# coding: utf-8
# Date: 2019/10/27
# wbq813@foxmail.com


class Results(object):
    """
    Default results class for wrapping decoded (from JSON) solr responses.

    Required ``decoded`` argument must be a Solr response dictionary.
    Individual documents can be retrieved either through ``docs`` attribute
    or by iterating over results instance.

    Optional ``next_page_query`` argument is a callable to be invoked when
    iterating over the documents from the result.

    Example::

        results = Results({
            'response': {
                'docs': [{'id': 1}, {'id': 2}, {'id': 3}],
                'numFound': 3,
            }
        })

        # this:
        for doc in results:
            print doc

        # ... is equivalent to:
        for doc in results.docs:
            print doc

        # also:
        list(results) == results.docs

    Note that ``Results`` object does not support indexing and slicing. If you
    need to retrieve documents by index just use ``docs`` attribute.

    Other common response metadata (debug, highlighting, qtime, etc.) are
    available as attributes.

    The full response from Solr is provided as the `raw_response` dictionary for
    use with features which change the response format.
    """

    def __init__(self, decoded, next_page_query=None):
        self.raw_response = decoded

        # main response part of decoded Solr response
        response_part = decoded.get("response") or {}
        self.docs = response_part.get("docs", ())
        self.hits = response_part.get("numFound", 0)

        # other response metadata
        self.debug = decoded.get("debug", {})
        self.highlighting = decoded.get("highlighting", {})
        self.facets = decoded.get("facet_counts", {})
        self.spellcheck = decoded.get("spellcheck", {})
        self.stats = decoded.get("stats", {})
        self.qtime = decoded.get("responseHeader", {}).get("QTime", None)
        self.grouped = decoded.get("grouped", {})
        self.nextCursorMark = decoded.get("nextCursorMark", None)
        self._next_page_query = self.nextCursorMark is not None \
                                and next_page_query or None

    def __len__(self):
        if self._next_page_query:
            return self.hits
        else:
            return len(self.docs)

    def __iter__(self):
        result = self
        while result:
            for d in result.docs:
                yield d
            result = result._next_page_query and result._next_page_query()