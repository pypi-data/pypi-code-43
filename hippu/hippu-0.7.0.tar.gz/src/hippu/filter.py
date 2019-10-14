import inspect
import logging
from hippu.utils import get_name

log = logging.getLogger(__name__)


class Filters:
    def __init__(self, filters, handler):
        self._filters = filters
        self._handler = handler
        self._index = -1
        self._length = len(filters)

    def __iter__(self):
         return self

    def __next__(self):
        self._index += 1

        if self._index < self._length:
            return self._filters[self._index]

        return None

    def __call__(self, req, res, ctx):
        filter_ = next(self)

        if filter_:
            log.debug("Applying '%s' filter.", get_name(filter_))
            return filter_(req, res, ctx, self)

        log.debug("Calling request handler.")

        try:
            value = self._handler(req, res, ctx)
        except TypeError as err:
            log.error(str(err))
            log.error("Please check {} '{}' route handler signature - expecting 'handler(req, res, ctx)'.".format(req.method, req.path))
