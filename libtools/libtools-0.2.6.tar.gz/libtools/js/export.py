import sys
import json
import inspect
from pygments import highlight, lexers, formatters
from libtools import logger


def export_iterobject(iterable, filename=None, logging=True):
    """
    Summary:
        pretty prints json, list, and tuple objects or exports iter
        object schema to filesystem object on the local filesystem

    Args:
        :iterable (dict): dictionary, list, tuple, or complex object
        :filename (str):  name of file to be exported (optional)

    Returns:
        True | False Boolean export status

    """
    def is_tty():
        """
        Summary:
            Determines if output is displayed to the screen or redirected
        Returns:
            True if tty terminal | False is redirected, TYPE: bool
        """
        return sys.stdout.isatty()

    try:

        if filename:

            with open(filename, 'w') as handle:

                try:

                    handle.write(json.dumps(iterable, indent=4, sort_keys=True))
                    logger.info(
                        '%s: Wrote %s to local filesystem location' %
                        (inspect.stack()[0][3], filename))

                except TypeError as e:
                    # serialize via string json native string conversion
                    handle.write(json.dumps(iterable, indent=4, sort_keys=True, default=str))

            handle.close()


        elif is_tty():

            try:

                # convert dict schema to json
                json_str = json.dumps(iterable, indent=4, sort_keys=True)

            except TypeError as e:
                # serialize via string json native string conversion
                json_str = json.dumps(iterable, indent=4, sort_keys=True, default=str)

            print(
                highlight(
                    json_str,
                    lexers.JsonLexer(),
                    formatters.TerminalFormatter()
                ).strip()
            )

            if logging:
                logger.info('{}: successful export to stdout'.format(inspect.stack()[0][3]))
            return True

        else:

            try:

                # print output, but not to stdout; possibly commandline redirect
                print(json.dumps(iterable, indent=4, sort_keys=True))

            except TypeError as e:
                # serialize via string json native string conversion
                print(json.dumps(iterable, indent=4, sort_keys=True, default=str))

    except OSError as e:
        logger.critical(
            '%s: export_file_object: error writing to %s to filesystem. Error: %s' %
            (inspect.stack()[0][3], filename, str(e)))
        return False
    if logging:
        logger.info('export_file_object: successful export to {}'.format(filename))
    return True
