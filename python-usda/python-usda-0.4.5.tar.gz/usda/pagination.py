
class RawPaginator(object):
    """
    Generator to paginate over list results and return JSON data
    """

    listkey = 'list'
    """
    Key of the list description object in the response JSON.
    See :class:`usda.pagination.RawNutrientReportPaginator`'s documentation
    for more information.

    :type: str
    """

    itemkey = 'item'
    """
    Key of the item list in the list description object of the response JSON.
    See :class:`usda.pagination.RawNutrientReportPaginator`'s documentation
    for more information.

    :type: str
    """

    def __init__(self, client, *request_args, **request_kwargs):
        r"""
        :param client: An API client to use for performing requests.
        :type client: usda.base.DataGovClientBase
        :param \*request_args: Arguments passed to the
           :meth:`usda.base.DataGovClientBase.run_request` method.
        :param \**request_kwargs: Keyword arguments passed to the
           :meth:`usda.base.DataGovClientBase.run_request` method.
        """

        self.client = client
        """
        An API client to use for performing requests.

        :type: usda.base.DataGovClientBase
        """

        self.data = {}
        """
        List description object returned from the last API request.

        :type: dict
        """

        self.request_args = request_args
        """
        Arguments passed to the
        :meth:`usda.base.DataGovClientBase.run_request` method.

        :type: tuple
        """

        self.request_kwargs = request_kwargs
        """
        Keyword arguments passed to the
        :meth:`usda.base.DataGovClientBase.run_request` method.

        :type: dict(str, object)
        """

        self.current_offset = request_kwargs.get('offset', 0)
        """
        Offset of the current page; the first index of the item that is
        returned in the current page.

        :type: int
        """

        self.max = request_kwargs.get('max', 30)
        """
        The maximum number of items returned with each page.

        :type: int
        """

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.data.get(self.itemkey, [])) < 1:
            if self.itemkey in self.data and \
                    self.current_offset >= self.data['end']:
                raise StopIteration
            self._fetch_next()
        return self.data[self.itemkey].pop(0)

    def _fetch_next(self):
        self.request_kwargs['offset'] = self.current_offset
        self.data = self.client.run_request(
            *self.request_args, **self.request_kwargs)[self.listkey]
        self.current_offset += self.max


class RawNutrientReportPaginator(RawPaginator):
    """
    This class provides a way to handle Nutrient Reports; as those reports
    are a list of food items containing specified nutrients, the endpoint is
    paginated in a similar way as classic list endpoints.

    Paginated responses are usually structured in the following way:

    .. code:: json

       {
           "list": {
               "start": "...",
               "offset": "...",
               "total": "...",
               "item": []
           }
       }

    ``list`` holds all the list data; we call it the "list description object".
    Inside this object, the ``item`` list is the list of items returned in
    this page.

    However, in Nutrient Reports, the paginated reponse uses ``report`` as the
    list description object and ``foods`` as the food items list.
    To solve this use case, this class changes the
    :attr:`usda.pagination.RawPaginator.listkey` and
    :attr:`usda.pagination.RawPaginator.itemkey` class attributes to make them
    match those names.
    """

    listkey = 'report'
    """
    The nutrient report list description object's key.

    :type: str
    """

    itemkey = 'foods'
    """
    The nutrient report list description object's item list's key.
    """


class ModelPaginator(object):
    """
    Generator to paginate over list results and get custom models instead of
    raw JSON data.
    """

    def __init__(self, model, raw):
        """
        :param model: Any class that implements a
           ``from_response_data(response_data)`` static method.
        :param raw: A raw paginator to get raw JSON data from.
        :type raw: usda.pagination.RawPaginator
        """

        assert isinstance(raw, RawPaginator)
        self.raw = raw
        """
        A raw paginator used to fetch JSON data from.

        :type: usda.pagination.RawPaginator
        """

        self.model = model
        """
        Any class that implements a ``from_response_data(response_data)``
        static method and that will be used to return custom models.
        """

    def __iter__(self):
        return self

    def __next__(self):
        return self.model.from_response_data(next(self.raw))
