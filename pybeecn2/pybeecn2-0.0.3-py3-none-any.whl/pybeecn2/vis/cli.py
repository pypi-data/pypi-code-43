import argparse
from pybeecn2.vis.run import main


def setup_map_parser(subp, parents):
    """

    :param subp:
    :param parents:
    :return:
    """

    parser = subp.add_parser('map',
                             formatter_class=argparse.RawDescriptionHelpFormatter,
                             description=setup_map_parser.__doc__,
                             help='view the map of beecn sites',
                             parents=parents)
    # Add arguments to the parser
    parser.add_argument('--show', default=False, action='store_true', help='show the plots during runtime')
    parser.add_argument('--directory', required=True,
                        help='directory where to store the files generated from the analysis')
    parser.add_argument('--column', '-c', default='Total', type=str)
    parser.add_argument('--boundaries', required=True, help='Geographic boundaries for the map to plot')
    parser.add_argument('--points', required=True, help='The points to add to the map')
    parser.set_defaults(func=main)


def __argparse__(subp, parents):

    setup_map_parser(subp, parents)