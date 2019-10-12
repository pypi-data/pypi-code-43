"""This module glues all components together"""

import distutils.dir_util as dir_util
import logging
import os
import sys
from pathlib import Path

from melthon.data import get_yml_data
from melthon.middleware import MWLoader
from melthon.middleware import MWStep
from melthon.template import render_templates


def clean(output_path: Path):
    """Deletes generated and temporary files"""
    if output_path.is_dir():
        dir_util.remove_tree(output_path)
        logging.debug('Removed output folder "%s"', output_path)
    else:
        logging.info('Output folder "%s" not found. Nothing deleted.', output_path)


def build(templates_path: Path, static_path: Path, data_path: Path, middleware_path: Path, output_path: Path,
          pretty_urls: bool):
    # Check if mandatory templates_path exist
    if not templates_path.is_dir():
        logging.error('Configured templates folder "%s" doesn\'t exist', templates_path)
        exit(1)

    # Initial context
    context = {}
    if data_path.is_dir():
        logging.info('Loading YAML data files ...')
        context['data'] = get_yml_data(data_path)
    else:
        logging.warning('Configured data folder "%s" doesn\'t exist. Skipping data load.', data_path)

    # Load middlewares
    mws = None
    if middleware_path.is_dir():
        # Add current directory to path.
        # This is required to be able to load the middlewares
        sys.path.append(os.getcwd())

        # Load middlewares
        mws = MWLoader(middleware_path)
    else:
        logging.warning('Configured middleware folder "%s" doesn\'t exist. Skipping middleware execution.',
                        middleware_path)

    # Delete and recreate output folder
    logging.info('Cleaning temporary and output folders ...')
    clean(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # Execute middlewares "before" step
    if mws is not None:
        context = mws.execute_chain(MWStep.BEFORE, context)
        logging.debug('Context after middlewares "before" step: %s', repr(context))

    # Render pages
    logging.info('Rendering pages ...')
    render_templates(templates_path, output_path, context, pretty_urls)

    # Copy static assets to output
    if static_path.is_dir():
        logging.info('Copying static assets to output ...')
        static_dir = str(static_path.resolve())
        output_dir = str(output_path.resolve())
        dir_util.copy_tree(static_dir, output_dir, update=True)
    else:
        logging.warning('Configured static folder "%s" doesn\'t exist. Skipping copy to output.', static_path)

    # Execute middlewares "after" step
    if mws is not None:
        context = mws.execute_chain(MWStep.AFTER, context)
        logging.debug('Context after middlewares "after" step: %s', repr(context))
