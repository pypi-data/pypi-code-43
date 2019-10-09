import logging

from converter import converters

logger = logging.getLogger(__name__)

AVAILABLE_CONVERTERS = {
    'erudit_ps': {
        'erudit_article': {
            'converter': converters.eruditps2eruditarticle,
            'output_format': 'xml'
        },
        'html': {
            'converter': converters.eruditps2html,
            'output_format': 'html'
        },
        'pdf': {
            'converter': converters.eruditps2pdf,
            'output_format': 'pdf'
        },
        'crossref': {
            'converter': converters.eruditps2crossref,
            'output_format': 'xml'
        }
    },
    'erudit_article': {
        'erudit_ps': {
            'converter': converters.eruditarticle2eruditps,
            'output_format': 'xml'
        },
        'html': {
            'converter': converters.eruditarticle2html,
            'output_format': 'html'
        },
        'pdf': {
            'converter': converters.eruditarticle2pdf,
            'output_format': 'pdf'
        },
        'crossref': {
            'converter': converters.eruditarticle2crossref,
            'output_format': 'xml'
        }
    },
    'texture': {
        'html': {
            'converter': converters.texture2html,
            'output_format': 'html'
        },
        'pdf': {
            'converter': converters.texture2pdf,
            'output_format': 'pdf'
        }
    }
}


class ConverterExceptions(Exception):
    pass


class UnsupportedConvertion(ConverterExceptions):
    pass


def print_available_converters():

    print('origin => destination')
    for origin_name, destiny in AVAILABLE_CONVERTERS.items():
        for destiny_name in destiny:
            print('%s => %s' % (origin_name, destiny_name))


def check_support(from_xml, to):

    if from_xml not in AVAILABLE_CONVERTERS:
        raise UnsupportedConvertion(
            'XML %s is unknown' % (from_xml)
        )

    if to not in AVAILABLE_CONVERTERS[from_xml]:
        raise UnsupportedConvertion(
            'XML %s can not be derivate from XML %s' % (to, from_xml)
        )


def convert(source, from_source, to, custom_styles=None, pagedjs_support=False):
    """
    param source: Path to the original XML intended to be converted to the output format specified in the parameter "to" 
    param from_xml: XML format of the origin XML file
    param to: format to be delivered
    param custom_style: css (cascading style sheet) to format the outputs. Works only for HTML and PDF outputs
    """

    logger.debug('Checking support to convert from %s to %s' % (from_source, to))
    check_support(from_source, to)

    if AVAILABLE_CONVERTERS[from_source][to]['output_format'] == 'html':
        return AVAILABLE_CONVERTERS[from_source][to]['converter'](
            source, custom_styles=custom_styles, pagedjs_support=pagedjs_support
        )
    if AVAILABLE_CONVERTERS[from_source][to]['output_format'] == 'pdf':
        return AVAILABLE_CONVERTERS[from_source][to]['converter'](source, custom_styles=custom_styles)

    return AVAILABLE_CONVERTERS[from_source][to]['converter'](source)
