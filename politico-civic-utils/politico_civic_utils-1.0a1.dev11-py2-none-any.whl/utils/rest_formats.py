# Imports from other dependencies.
from rest_framework.settings import api_settings


REST_FORMAT_PARSERS = {
    parser_klass.renderer_class.format: parser_klass
    for parser_klass in api_settings.DEFAULT_PARSER_CLASSES
    if hasattr(parser_klass, "renderer_class")
}

REST_FORMAT_RENDERERS = {
    format_str: parser_klass.renderer_class
    for format_str, parser_klass in REST_FORMAT_PARSERS.items()
}
