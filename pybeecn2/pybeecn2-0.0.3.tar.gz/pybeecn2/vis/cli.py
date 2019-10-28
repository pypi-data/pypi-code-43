"""
This work was authored by Gabriel McBride in support
of Portland Open Data Program and Portland Bureau of
Emergency Management BEECN Program. The effort was
conducted as a use case for the student's masters
project to study the interaction between Systems
Engineering and Data Science activities.
"""

import argparse
from pybeecn2.vis.run import main

pop_list = ['Total_Pop_5_n_over', 'Spanish', 'Russian', 'Other_Slavic', 'Other_Indic',
            'Other_Indo_European', 'Chinese', 'Japanese', 'Korean', 'Mon_Khmer_Cambodian',
            'Laotian', 'Vietnamese', 'Other_Asian', 'Tagalog', 'Other_Pacific_Island',
            'Arabic', 'African']


def setup_beecn_parser(subp, parents):
    """
    BEECN Command Line Interface (CLI) Application
-------------------------------------------------------------
Purpose:
Provide a command line interface for viewing map boundary
data and points along with relevant population data.

-------------------------------------------------------------
    :param subp:
    :param parents:
    :return:
    """
    # Create the parser
    parser = subp.add_parser('map', formatter_class=argparse.RawDescriptionHelpFormatter,
                             description=setup_beecn_parser.__doc__,
                             help='view the locations of BEECN sites', parents=parents)

    # Add arguments to the parser
    parser.add_argument('--show',
                        default=False,
                        action='store_true',
                        help='show the plots during runtime')
    parser.add_argument('--directory',
                        required=True,
                        help='directory where to store the files generated from the analysis')
    parser.add_argument('--demographic',
                        default='Total_Pop_5_n_over',
                        choices=pop_list,
                        type=str)
    parser.add_argument('--boundaries',
                        required=True,
                        help='Geographic boundaries for the map to plot')
    parser.add_argument('--points',
                        required=True,
                        help='The points to add to the map')
    parser.set_defaults(func=main)

def __argparse__(subp, parents=[]):
    """BEECN Application
    Put a description here
    :param subp:
    :param parents:
    :return:
    """

    setup_beecn_parser(subp, parents)

