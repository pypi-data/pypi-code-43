# Imports from civic_utils.
from civic_utils.utils.rest_formats import REST_FORMAT_PARSERS
from civic_utils.utils.rest_formats import REST_FORMAT_RENDERERS


DEFAULT_FIXTURE_ACL = 'bucket-owner-full-control'

TEMP_DIR = 'tmp'

ALLOWED_SERIALIZER_FORMATS = list(REST_FORMAT_PARSERS.keys())

FORMAT_EXTENSION_MAP = {
    'json': 'json'
}

FORMAT_MIME_MAP = dict(
    (format_str, renderer_klass.media_type)
    for format_str, renderer_klass in REST_FORMAT_RENDERERS.items()
)
