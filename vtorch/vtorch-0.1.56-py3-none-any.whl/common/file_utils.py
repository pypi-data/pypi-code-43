import os
import logging
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, Tuple, Union, IO, Callable, Set

CACHE_ROOT = Path(os.getenv('VTORCH_CACHE_ROOT', Path.home() / '.vtorch'))
CACHE_DIRECTORY = str(CACHE_ROOT / "cache")

logger = logging.getLogger(__name__)


def cached_path(url_or_filename: Union[str, Path], cache_dir: str = None) -> str:
    """
    Given something that might be a URL (or might be a local path),
    determine which. If it's a URL, download the file and cache it, and
    return the path to the cached file. If it's already a local path,
    make sure the file exists and then return the path.
    """
    if cache_dir is None:
        cache_dir = CACHE_DIRECTORY
    if isinstance(url_or_filename, Path):
        url_or_filename = str(url_or_filename)

    url_or_filename = os.path.expanduser(url_or_filename)
    parsed = urlparse(url_or_filename)

    # if parsed.scheme in ('http', 'https', 's3'):
    #     # URL, so get it from the cache (downloading if necessary)
    #     return get_from_cache(url_or_filename, cache_dir)
    if os.path.exists(url_or_filename):
        # File, and it exists.
        return url_or_filename
    elif parsed.scheme == '':
        # File, but it doesn't exist.
        raise FileNotFoundError("file {} not found".format(url_or_filename))
    else:
        # Something unknown
        raise ValueError("unable to parse {} as a URL or as a local path".format(url_or_filename))