"""Sync files from a Flywheel project to a local folder or an S3 bucket.

examples:
  fw sync fw://group/project s3://bucket/prefix
"""
import argparse
import logging
import re
import sys

import fs.filesize
from .. import sdk_impl

from ..sync.fw_src import FWSource
from ..sync.os_dst import OSDestination
from ..sync.s3_dst import S3Destination
from ..sync.queue import SyncQueue


log = logging.getLogger(__name__)


def add_command(subparsers, parents):
    """Add fw sync command parser"""
    parser = subparsers.add_parser(
        'sync', parents=parents,
        help='Sync files from Flywheel to storage',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__)

    parser.add_argument(
        'src', metavar='PROJECT',
        help='Flywheel project to sync from (fw://group/project)')
    parser.add_argument(
        'dst', metavar='STORAGE', nargs='?',
        help='Destination to sync to (/local/path or s3://bucket)')

    parser.add_argument(
        '-i', '--include', metavar='T', default=[], action='append',
        help='Sync only the specified types (eg.: -i dicom)')
    parser.add_argument(
        '-e', '--exclude', metavar='T', default=[], action='append',
        help='Skip the specified types (eg.: -e nifti -e qa)')
    parser.add_argument(
        '-a', '--analyses', action='store_true',
        help='Include analyses')
    parser.add_argument(
        '-m', '--metadata', action='store_true',
        help='Include metadata')
    parser.add_argument(
        '-x', '--full-project', action='store_true',
        help='Include analyses and metadata')

    parser.add_argument(
        '-z', '--no-unpack', dest='unpack', action='store_false',
        help='Keep zipped DICOMs intact (default: extract)')
    parser.add_argument(
        '-l', '--list-only', action='store_true',
        help='Show folder tree on source instead of syncing')
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='Show individual files with --list-only')
    parser.add_argument(
        '-n', '--dry-run', action='store_true',
        help='Show what would be synced without transferring files')
    parser.add_argument(
        '-j', '--jobs', type=int, metavar='N', default=4,
        help='The number of concurrent jobs to run (default: 4)')

    parser.add_argument(
        '--delete', action='store_true',
        help='Delete extra files from destination')

    parser.set_defaults(func=sync)
    parser.set_defaults(parser=parser)
    return parser


def sync(args):
    """Run fw sync for the parsed cli args"""
    fw = sdk_impl.create_flywheel_client()
    ticket = get_download_ticket(fw, args)
    strip_project = args.src.endswith('/')  # strip root-dir based on trailing slash (like rsync)
    src = FWSource(fw, ticket.ticket, strip_project=strip_project, unpack=args.unpack)
    src_files = get_filedict(args.src, src)

    if args.list_only or args.dst is None:  # print src if dst not given (like rsync)
        print_tree(src_files.values(), verbose=args.verbose)
        sys.exit(0)

    s3_match = re.match(r's3://(?P<bucket>[^/]+)(?P<prefix>.*)', args.dst)
    if s3_match:
        # NOTE make sure prefix doesn't start but ends with slash for dir-like listing on s3
        dst = S3Destination(s3_match.group('bucket'), s3_match.group('prefix').strip('/') + '/')
    else:
        dst = OSDestination(args.dst)  # simply use args.dst as the destination path for os
    dst_files = get_filedict(args.dst, dst)

    queue = SyncQueue(args.jobs, dst, assume_yes=args.yes, dry_run=args.dry_run)
    queue.start()
    for name, src_file in src_files.items():  # create/update
        dst_file = dst_files.pop(name, None)
        queue.store(src_file, dst_file)
    if args.delete:
        for dst_file in dst_files.values():  # delete
            queue.delete(dst_file)
    queue.wait_for_finish()
    queue.shutdown()
    if args.delete:
        dst.cleanup()  # final cleanup (os: empty dirs, s3: last bulk delete)


def get_download_ticket(fw, args):
    """Get download ticket"""
    project = fw.lookup(sdk_impl.parse_resolver_path(args.src))
    if project.container_type != 'project':
        args.parser.error(f'{args.src} is not a project')
    payload = {'nodes': [{'level': 'project', '_id': project.id}]}
    filters = []
    if args.include:
        filters.append({'types': {'+': args.include}})
    if args.exclude:
        filters.append({'types': {'-': args.exclude}})
    if filters:
        payload['filters'] = filters
    params = {'type': 'full', 'prefix': ''}
    if args.analyses or args.full_project:
        params['analyses'] = True
    if args.metadata or args.full_project:
        params['metadata'] = True
    return fw.create_download_ticket(payload, **params)


def get_filedict(fs_url, files, report_batch=100, fh=sys.stdout):
    """Return {name: file} dict for an src/dst and report progress"""
    file_dict = {}
    total_size = 0
    total_count = 0

    def report(fs_url, size, count, newline='\r'):
        # TODO optimization to terminal size
        size_str = fs.filesize.traditional(size)
        fh.write(f'{fs_url} ({size_str} / {count} files)'.ljust(72))
        fh.write(newline)
        fh.flush()

    for file in files:
        file_dict[file.name] = file
        total_size += file.size
        total_count += 1
        if total_count % report_batch == 0:
            report(fs_url, total_size, total_count)
    report(fs_url, total_size, total_count, newline='\n')
    return file_dict


def print_tree(files, verbose=False, fh=sys.stdout):
    """Print a tree representation of files"""
    utf8 = fh.encoding == 'UTF-8'
    none_str = '│  ' if utf8 else '|  '
    node_str = '├─ ' if utf8 else '|- '
    last_str = '└─ ' if utf8 else '`- '

    def pprint_tree(node, prefix='', last=True):
        print(prefix, last_str if last else node_str, node, file=fh, sep='')
        prefix += '   ' if last else none_str
        child_count = len(node.children)
        children = sorted(node.children.values(), key=Node.sort_key)
        for i, child in enumerate(children):
            last = i == (child_count - 1)
            pprint_tree(child, prefix, last)

    root = Node('root')
    for file in files:
        node = root
        parts = file.name.split('/')
        for dirname in parts[:-1]:
            node = node.children.setdefault(dirname, Node(dirname))
        if verbose:  # add files as leaf nodes
            filename = parts[-1]
            node.children.setdefault(filename, Node(filename, size=file.size))
        else:  # sum file size and count in parent node
            node.size += file.size
            node.files += 1

    for child in sorted(root.children.values(), key=Node.sort_key):
        pprint_tree(child)


class Node:
    """File tree node"""
    # pylint: disable=too-few-public-methods

    __slots__ = ('name', 'size', 'files', 'children')

    def __init__(self, name, size=0, files=0):
        self.name = name
        self.size = size
        self.files = files
        self.children = {}

    def __str__(self):
        hrsize = fs.filesize.traditional(self.size)
        plural = 's' if self.files > 1 else ''
        if self.size and self.files:  # container w/ files
            return f'{self.name} ({hrsize} / {self.files} file{plural})'
        if self.size:  # file
            return f'{self.name} ({hrsize})'
        return self.name  # container w/o files

    def sort_key(self):
        """Show leaf nodes first (eg. files, metadata sidecars)"""
        return len(self.children) > 0, self.name
