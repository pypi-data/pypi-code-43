import argparse


def init_parser(root_parser):
    return root_parser.add_parser(
        'init',
        help='Initialize a new git repo with support for the branching model.'
    )


def feature_parser(root_parser):
    parser = root_parser.add_parser(
        'feature', help='Manage your feature branches.')

    subparsers_feature = parser.add_subparsers(
        dest='feature_cmd', help='Feature branch management')

    parser_feature_start = subparsers_feature.add_parser('start')
    parser_feature_finish = subparsers_feature.add_parser('finish')
    parser_feature_delete = subparsers_feature.add_parser('delete')

    # FEATURE START
    parser_feature_start.add_argument('name', type=str)
    parser_feature_start.add_argument(
        'base', type=str, nargs='?', default='develop')

    # FEATURE FINISH
    parser_feature_finish.add_argument('name', type=str)
    parser_feature_finish.add_argument(
        '--merge', action='store_true', help='try to trigger Gitlab merge')

    # FEATURE DELETE
    parser_feature_delete.add_argument('name', type=str)

    return parser


def release_parser(root_parser):
    parser = root_parser.add_parser(
        'release', help='Manage your release branches.')

    subparsers_release = parser.add_subparsers(
        dest='release_cmd', help='Release branch management')

    parser_release_start = subparsers_release.add_parser('start')
    parser_release_finish = subparsers_release.add_parser('finish')
    parser_release_delete = subparsers_release.add_parser('delete')

    # RELEASE START
    parser_release_start.add_argument('version', type=str)
    parser_release_start.add_argument(
        'base', type=str, nargs='?', default='develop')

    # RELEASE FINISH
    parser_release_finish.add_argument('version', type=str)

    # RELEASE DELETE
    parser_release_delete.add_argument('version', type=str)

    return parser


def CommandParser():
    parser = argparse.ArgumentParser(prog='git gud')
    subparsers = parser.add_subparsers(dest='parser_cmd')
    init_parser(subparsers)
    feature_parser(subparsers)
    release_parser(subparsers)

    # parser_bugfix = subparsers.add_parser('bugfix', help='Manage your bugfix branches.')
    # parser_hotfix = subparsers.add_parser('hotfix', help='Manage your hotfix branches.')
    # parser_support = subparsers.add_parser('support', help='Manage your support branches.')
    # parser_log = subparsers.add_parser('log', help='Show log deviating from base branch.')

    return parser
