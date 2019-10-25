# -*- coding: utf-8 -*-
"""
Mapping Learning execution script


This script is the main entry to play with mapping learning. Just specify a
well-formatted configuration file and run.

The configuration file is described on
https://bitbucket.org/thomas_a/maplearn/wiki/configuration. A few examples of
configuration are also available in "examples" sub-folder.

Example::

    $ python run.py -c /path/to/configfile

"""
from __future__ import print_function
from __future__ import unicode_literals
import os
import sys

from maplearn.app.main import Main
from maplearn.app.reporting import ReportWriter
from maplearn.app.cli import cfg as config
from maplearn import logger

def run():
    """
    Run the application with the given configuration.
    """
    logger.info('maplearn: start !')

    if config.check() != 0:
        return None
    # redirection des print vers 1 fichier
    report_file = os.path.join(config.io['output'], 'index')
    report_writer = ReportWriter(report_file)
    sys.stdout = report_writer

    print(config)
    appli = Main(config.io['output'], codes=config.codes, na=config.io['na'],
                 **config.process)

    # TODO: ugly PATCH to remove ASAP
    if config.process['type'] == 'clustering' and \
            config.io['samples'] is None:
        config.io['samples'] = config.io['data']

    appli.load(source=config.io['samples'], **config.io)
    if config.io['data'] is not None:
        appli.load_data(config.io['data'], features=config.io['features'])
    #basename = os.path.splitext(os.path.basename(config.io['samples']))[0]
    #appli.dataset.plot(os.path.join(config.io['output'],
    #                              'sig_%s.png' % basename))
    #print(appli.dataset)
    appli.preprocess(**config.preprocess)
    appli.process(optimize=config.process['optimize'],
                  predict=config.process['predict'])

    report_writer.close()
    # export configuration in output folder
    config.write(os.path.join(config.io['output'], 'configuration.cfg'))
    logger.info('maplearn: end.')

if __name__ == "__main__":
    run()
