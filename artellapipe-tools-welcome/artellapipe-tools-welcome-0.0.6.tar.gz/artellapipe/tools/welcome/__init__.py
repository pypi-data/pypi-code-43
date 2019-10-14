#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for artellapipe-tools-welcome
"""

import os
import inspect
import logging.config


def init(do_reload=False):
    """
    Initializes module
    """

    logging.config.fileConfig(get_logging_config(), disable_existing_loggers=False)

    import sentry_sdk
    sentry_sdk.init("https://b0114e6428964b20ae057087f5fda45b@sentry.io/1763194")

    from tpPyUtils import importer

    class ArtellaWelcome(importer.Importer, object):
        def __init__(self):
            super(ArtellaWelcome, self).__init__(module_name='artellapipe.tools.welcome')

        def get_module_path(self):
            """
            Returns path where tpNameIt module is stored
            :return: str
            """

            try:
                mod_dir = os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename)
            except Exception:
                try:
                    mod_dir = os.path.dirname(__file__)
                except Exception:
                    try:
                        import tpDccLib
                        mod_dir = tpDccLib.__path__[0]
                    except Exception:
                        return None

            return mod_dir

    packages_order = []

    artellawelcome_importer = importer.init_importer(importer_class=ArtellaWelcome, do_reload=False)
    artellawelcome_importer.import_packages(order=packages_order, only_packages=False)
    if do_reload:
        artellawelcome_importer.reload_all()

    create_logger_directory()


def run(project, do_reload=False):
    """
    Run ArtellaWelcome Tool
    :param project: ArtellaProject
    :param do_reload: bool
    :return: ArtellaManager
    """

    from artellapipe.utils import exceptions

    try:
        init(do_reload=do_reload)
        from artellapipe.tools.welcome import welcome
        win = welcome.run(project=project)
        return win
    except RuntimeError as exc:
        exceptions.capture_sentry_exception(exc)


def create_logger_directory():
    """
    Creates artellapipe-gui logger directory
    """

    artellapipe_logger_dir = os.path.normpath(os.path.join(os.path.expanduser('~'), 'artellapipe', 'logs'))
    if not os.path.isdir(artellapipe_logger_dir):
        os.makedirs(artellapipe_logger_dir)


def get_logging_config():
    """
    Returns logging configuration file path
    :return: str
    """

    create_logger_directory()

    return os.path.normpath(os.path.join(os.path.dirname(__file__), '__logging__.ini'))


def get_logging_level():
    """
    Returns logging level to use
    :return: str
    """

    if os.environ.get('ARTELLAPIPE_TOOLS_WELCOME_LOG_LEVEL', None):
        return os.environ.get('ARTELLAPIPE_TOOLS_WELCOME_LOG_LEVEL')

    return os.environ.get('ARTELLAPIPE_TOOLS_WELCOME_LOG_LEVEL', 'WARNING')
