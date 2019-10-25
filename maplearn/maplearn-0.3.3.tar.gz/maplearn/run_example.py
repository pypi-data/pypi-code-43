# -*- coding: utf-8 -*-
"""
**Mapping Learning : examples**

This script is a good way to discover Mapping Learning possibilities. Using
configuration files available in "examples" subfolder and datasets included in
"datasets" sub-folder, you will see what can do this application.

Code inside "run_example.py" can be used through a script called
"maplearn_example" 

Example:
        * Asks the user to choose which examples(s) he wants to test:

            $ maplearn_example

        * Execute 3rd example (CLI way):

            $ maplearn_example 3

        * Launch every available examples:

            $ maplearn_example all

"""
from __future__ import print_function
import os
import sys
import subprocess
import inspect
from glob import glob

from maplearn.app.config import Config

# application path
DIR_APP = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
if __name__ == '__main__' and __package__ is None:
    os.sys.path.append(DIR_APP)

# list of available examples
LST_EX = glob(os.path.join(DIR_APP, 'examples', 'example*.cfg'))
LST_EX.sort()

# Number corresponding to examples
NB_EX = [os.path.basename(i)[7:-4] for i in LST_EX]

def run_example(*ex):
    """
    Run one or several examples based on their number

    Arg:
        * number (str) : identifies the example to run
    """
    if 'all' in ex:
        ex = NB_EX
    for i in ex:
        run_cfg(LST_EX[NB_EX.index(i)], DIR_APP)

def run_cfg(cfg_file, path):
    """
    Run one of available examples in "examples" folder based on a
    configuration file

    Args:
        * cfg_file (str) : path to the configuration file
        * path (str) : path to run.py script (that launches the application)
    """
    if not os.path.exists(cfg_file):
        print('Configuration file %s is missing => Give up.')
        return None
    subprocess.call(["python",
                     os.path.join(path, "run.py"), "-c", cfg_file])

def main():
    """
    Main script to run included examples
    """
    if len(sys.argv) > 1:
        lst_run = sys.argv[1:]
        run_example(*lst_run)
    elif len(sys.argv) == 1:
        for i in LST_EX:
            print(Config(i))
        MSG = 'Choisissez un exemple (%s-%s) :' % (NB_EX[0], NB_EX[-1])
        #PYTHON2/3 comptability
        try:
            reponse = raw_input(MSG).strip()
        except NameError:
            reponse = input(MSG).strip()
        again = True
        while again:
            again = False
            if reponse == 'q':
                sys.exit(0)
            elif reponse in NB_EX:
                run_example(reponse)
            else:
                again = True
                #PYTHON2/3 comptability
                try:
                    reponse = raw_input(MSG).strip()
                except NameError:
                    reponse = input(MSG).strip()

if __name__ == '__main__':
    main()
