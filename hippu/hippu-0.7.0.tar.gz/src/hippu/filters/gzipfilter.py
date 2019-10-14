import gzip
import logging
import re
import time

from hippu import HTTP


log = logging.getLogger(__name__)


class GzipFilter:
    """ Compress respone content.

    Usage:
        Compress all HTTP get repsonces.
        >>> service.add_filter(GzipFilter)

        Compress all HTTP GET responses:
        >>> service.add_filter(GzipFilter(methods=['GET']))

        Using multiple filters in conjunction:
        >>> service.add_filter(GzipFilter(match='.css'))
        >>> service.add_filter(GzipFilter(match='.html'))

    See:
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Encoding
    """

    def __init__(self, methods=['GET', 'HEAD'], match=None, min_size=0, verbose=True):
        self._pattern = match # Pattern to match.
        self._min_size = min_size # Minimum size to trigger compression.
        self._verbose = verbose # Write debug log.
        self._target_methods = methods # Targeted HTTP methods (e.g., ['GET', 'HEAD'])

    def __call__(self, req, res, ctx, next):
        next(req, res, ctx)

        # Filter is applied only to targeted HTTP methods.
        if req.method.upper() not in self._target_methods:
            return

        # Make sure the content is not already compressed.
        if res.headers.get(HTTP.CONTENT_ENCODING, None) == HTTP.GZIP:
            return

        orig_size = len(res) / 1000

        # Don't apply filter to responses having smaller size than given
        # minimum size in kilo bytes.
        if orig_size < self._min_size:
            return

        # Target filter for selected paths.
        if self._pattern and not re.match(self._pattern, req.path):
            return

        t1 = time.time()

        if isinstance(res.content, bytes):
            res.content = gzip.compress(res.content)
        elif isinstance(res.content, str):
            res.content = gzip.compress(res.content.encode('utf-8'))
        else:
            return

        res.set_header(HTTP.CONTENT_ENCODING, HTTP.GZIP)

        if self._verbose:
            # Statistics
            gzip_size = len(res) / 1000
            ratio = round(1 - gzip_size / orig_size, 2) * 100
            duration = (time.time() - t1) * 1000

            # Compressing HTTP GET /index.html response from 0.21kb to 0.15kb took 0.137ms (30.0%).
            log.debug("Compressing %s response from %.2fkb to %.2fkb (%s%%) took %.2fms.", req, orig_size, gzip_size, ratio, duration)
