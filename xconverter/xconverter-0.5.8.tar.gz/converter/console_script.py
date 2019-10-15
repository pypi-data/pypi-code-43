import os
import sys
import argparse
import logging
import logging.config

from converter import engine
from converter.converters import EruditPS2PDFError

logger = logging.getLogger(__name__)

SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'DEBUG')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'console': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': LOGGING_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'console',
            'stream': sys.stdout
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': LOGGING_LEVEL,
            'propagate': False,
        },
        'converter': {
            'level': LOGGING_LEVEL,
            'propagate': True,
        }
    }
}

if SENTRY_DSN:
    LOGGING['handlers']['sentry'] = {
        'level': 'ERROR',
        'class': 'raven.handlers.logging.SentryHandler',
        'dsn': SENTRY_DSN,
    }
    LOGGING['loggers']['']['handlers'].append('sentry')


def write_to_file(xml, write_to):

    with open(write_to, 'wb') as file_to_write:

        file_to_write.write(xml)


def attach_suffix(file_name, suffix, output_format):

    splited = file_name.split('.')
    ext = splited[-1]
    splited[-1] = suffix
    splited.append(ext)

    splited[-1] = output_format

    return '.'.join(splited)


def run(source, from_source, to, suffix, custom_styles=None, pagedjs_support=False):

    for item in source:

        logger.info('Converting file %s from %s to %s' % (item, from_source, to))

        custom_styles = [os.path.abspath(i) for i in custom_styles] if custom_styles is not None else []

        try:
            document = engine.convert(
                item,
                from_source,
                to,
                custom_styles=custom_styles,
                pagedjs_support=pagedjs_support
            )
        except EruditPS2PDFError as e:
            logger.error('Fail to convert: %s', str(e))
            continue

        output_format = engine.AVAILABLE_CONVERTERS[from_source][to]['output_format']

        file_name = attach_suffix(item, suffix, output_format)

        write_to_file(document, file_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', nargs='*')
    parser.add_argument(
        '--converters',
        '-c',
        action='store_true',
        help='display available converters'
    )
    parser.add_argument(
        '--from_source',
        '-f',
        help='from source could be .xml or .dar files',
        choices=engine.AVAILABLE_CONVERTERS.keys()
    )
    parser.add_argument(
        '--to',
        '-t',
        help='the output format. It could be an XML or HTML according to the conversor selected'
    )
    parser.add_argument(
        '--output_dir',
        '-o',
        help='directory where the derivated XML files will be stored',
        default='.'
    )
    parser.add_argument(
        '--suffix',
        '-s',
        help='''suffix to be concatenated to the output XML files. If not'''
             '''specified, it will assume the value of --to_xml'''
    )
    parser.add_argument(
        '--custom_styles',
        '-x',
        nargs='*',
        help='''list of paths to a CSS file to customize the default PDF Cascading Style Sheets'''
             '''it is relevant only while producing PDF or HTML outputs'''
    )
    parser.add_argument(
        '--pagedjs_support',
        '-p',
        action="store_true",
        help='''apply pagedjs support for HTML outputs incluind paged.js and preview.css in the head of the html'''
    )

    parser.add_argument(
        '--log_level',
        '-l',
        help='Logging level',
        choices=['ERROR', 'WARNING', 'INFO', 'DEBUG'],
        default='INFO'
    )

    args = parser.parse_args()

    LOGGING['handlers']['console']['level'] = args.log_level
    for lg, content in LOGGING['loggers'].items():
        content['level'] = args.log_level

    logging.config.dictConfig(LOGGING)

    if args.converters is True:
        engine.print_available_converters()
        exit()

    disjunctor = False
    if not args.from_source:
        logger.info('parameter --from_source is required')
        disjunctor = True

    if not args.to:
        logger.info('parameter --to is required')
        disjunctor = True

    if disjunctor is True:
        exit()

    try:
        engine.check_support(args.from_source, args.to)
    except engine.UnsupportedConvertion as exp:
        logger.error(exp)

    if args.suffix is None:
        args.suffix = args.to

    run(
        args.source,
        args.from_source,
        args.to,
        args.suffix,
        args.custom_styles,
        args.pagedjs_support
    )
