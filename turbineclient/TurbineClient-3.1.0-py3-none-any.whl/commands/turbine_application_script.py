#!/usr/bin/env python
##########################################################################
# $Id: turbine_application_script.py 4480 2013-12-20 23:20:21Z boverhof $
# Joshua R. Boverhof, LBNL
# See LICENSE.md for copyright notice!
#
#   $Author: boverhof $
#   $Date: 2013-12-20 15:20:21 -0800 (Fri, 20 Dec 2013) $
#   $Rev: 4480 $
#
###########################################################################
import urllib.request
import urllib.error
import csv
import sys
import os
import json
import logging as _log
import optparse
from urllib.error import HTTPError
from turbine.commands import add_options, add_json_option, get_page, get_paging, _print_as_json, put_page, post_page,\
    _open_config, load_pages_json

SECTION = "Application"


def _print_list(all, verbose=False, out=sys.stdout):
    print("Total Applications: %d" % len(all), file=out)
    for j in range(len(all)):
        app = all[j]
        if not verbose:
            print("\t%s" % app['Name'], file=out)
            continue
        print("=="*30, file=out)
        print("%s" % (app['Name']), file=out)
        print("\tInputs", file=out)
        for i in range(len(app['Inputs'])):
            e = app['Inputs'][i]
            print("\t%d. %12s: %s" % (i+1, e['Name'], str(e)), file=out)


def main_list(args=None, func=_print_list):
    """List all application resources, by default print in human readable format.
    """
    op = optparse.OptionParser(usage="USAGE: %prog [options] CONFIG_FILE",
                               description=main_list.__doc__)
    add_options(op)
    add_json_option(op)
    (options, args) = op.parse_args(args)

    if len(args) != 1:
        op.error('expecting 1 argument')

    if options.json:
        func = _print_as_json

    configFile = _open_config(args[0])
    query = {}

    options.page = 1
    content = get_page(configFile, SECTION, **query)
    data = load_pages_json([content])
    if func:
        func(data, verbose=options.verbose)
    return data


if __name__ == "__main__":
    main_list()
