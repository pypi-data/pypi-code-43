import argparse
import getpass
import json
import logging
from argparse import ArgumentParser, ArgumentTypeError

from .connection import DSMConnection
from .process import Process
from .task import Task

LOG = logging.getLogger(__name__)


class Options:

    def __init__(self):
        self.process = Process()
        self._init_parser()

    def _init_parser(self):
        """Define arguments for the CLI."""
        self.parser = ArgumentParser(description='Manage Dell Storage Manager objects via REST API.')

        self.parser.add_argument('--dsm_host',
                                 default='sc-data-ma.admin.cam.ac.uk', type=str,
                                 help='DSM hostname. Default: sc-data-ma.admin.cam.ac.uk')
        self.parser.add_argument('--dsm_port',
                                 default=3033,
                                 help='DSM port. Default: 3033')
        self.parser.add_argument('--dsm_user',
                                 type=str,
                                 help='DSM Data Collector username')
        self.parser.add_argument('--dsm_password',
                                 type=str,
                                 help='DSM Data Collector password')
        self.parser.add_argument('--is_secure',
                                 type=str2bool,
                                 default=False,
                                 help='Secure connection. Default: False')
        self.parser.add_argument('--record_config',
                                 type=str2bool,
                                 default=False,
                                 help='Record multipath and file system config details.\
                                 Default: False (do not record system config details)')
        self.parser.add_argument('--file',
                                 type=open,
                                 action=LoadFromFile,
                                 help='Read arguments from json file')

        self.subparsers = self.parser.add_subparsers(dest='subparser')

        # list dell sc objects
        self.parser_list = self.subparsers.add_parser('list',
                                                      help='List Dell SC objects. \
                                                      Example: ucamdsm --dsm_user user --dsm_password abc123 list \
                                                      --object scs')
        self.parser_list.add_argument(
            '--object',
            required=True,
            choices=['scs', 'servers', 'volumes', 'snapshots', 'volFolders', 'snapshotProfiles', 'recycledVols'])
        self.parser_list.add_argument('--output',
                                      choices=['json'],
                                      help='Format of the output. Supported formats: json')

        # delete_volume
        self.parser_delete_volume = self.subparsers.add_parser('delete_volume',
                                                               help='Delete Dell SC Volume. \
                                                               Example: ucamdsm --dsm_user user \
                                                               --dsm_password abc123 delete_volume \
                                                               --vol_wwn 12345')
        self.parser_delete_volume.add_argument('--vol_wwn',
                                               required=True,
                                               help='ID of the volume to delete. \
                                               Must be mapped to local server')
        self.parser_delete_volume.add_argument('--recycle',
                                               type=str2bool,
                                               default=True,
                                               help='Recycle the volume or delete it permanently. \
                                               Default: True (recycle the volume)')

        # replace_volume
        self.parser_replace_volume = self.subparsers.add_parser('replace_volume',
                                                                help='Clone the volume mounted on source \
                                                                mountpoint and mount it on destination mountpoint. \
                                                                Then, delete the volume was initially mounted on \
                                                                destination mountpoint. Example: ucamdsm --dsm_user \
                                                                user  --dsm_password abc123 replace_volume \
                                                                --src_mp /src --dst_mp /dst')
        self.parser_replace_volume.add_argument('--src_mp',
                                                required=True,
                                                help='Source mountpoint. Must be on local server')
        self.parser_replace_volume.add_argument('--dst_mp',
                                                required=True,
                                                help='Destination mountpoint. Must be on local server')

        # clone_volume
        self.parser_clone_volume = self.subparsers.add_parser('clone_volume',
                                                              help='Create a snapshot with label of a volume \
                                                              with WWN, create a view volume from the snapshot, \
                                                              then, map the view volume to local server and \
                                                              mount it on target mountpoint. Example: ucamdsm \
                                                              --dsm_user user --dsm_password abc123 clone_volume \
                                                              --vol_wwn 12345 --replay_label test1 --target_mp /target')
        self.parser_clone_volume.add_argument('--vol_wwn',
                                              required=True,
                                              help='WWN of the volume from which to create the snapshot')
        self.parser_clone_volume.add_argument('--replay_label',
                                              required=True,
                                              help='Snapshot label.')
        self.parser_clone_volume.add_argument('--target_mp',
                                              required=True,
                                              help='The mountpoint that the view volume will be mounted on. \
                                              Must be on local server')

        # create_snapshot
        self.parser_create_snapshot = self.subparsers.add_parser('create_snapshot',
                                                                 help='Create a snapshot of the volume mounted on \
                                                                 a given mountpoint. Example: ucamdsm --dsm_user \
                                                                 user --dsm_password abc123 create_snapshot --mp /mp \
                                                                 --replay_label test1 --retention 5')
        self.parser_create_snapshot.add_argument('--mp',
                                                 required=True,
                                                 help='The mountpoint where the volume is mounted. \
                                                 Must be on local server')
        self.parser_create_snapshot.add_argument('--replay_label',
                                                 required=True,
                                                 help='Snapshot label')
        self.parser_create_snapshot.add_argument('--retention',
                                                 required=True,
                                                 help='Retention period of the snapshot to create, in days')

        # deleted the recycled vols whose wwns are listed in a file
        self.parser_delete_recycled_vols = self.subparsers.add_parser('delete_recycled_vols',
                                                                      help='Delete recycled volumes whose WWNs are listed in a file. \
                                                                      Example: ucamdsm --dsm_user user --dsm_password \
                                                                      abc123 delete_recycled_vols --wwns_file \
                                                                      /tmp/recycled_vols_wwns.txt')
        self.parser_delete_recycled_vols.add_argument('--wwns_file',
                                                      required=True,
                                                      help='File containing the WWNs of the recycled volumes \
                                                      to be deleted.')

    def parse(self, args=None):
        """Parse given arguments and execute an action accordingly."""
        result = None
        self.known, self.unknown = self.parser.parse_known_args(args)[:]

        if len(self.unknown) != 0:
            LOG.error('*WARN* Unknown args received: %s.', repr(self.unknown))
            return False

        if self.known.subparser is None or \
                self.known.subparser not in ['list', 'delete_volume',
                                             'replace_volume', 'clone_volume', 'create_snapshot',
                                             'delete_recycled_vols']:
            LOG.error('No subcommand is specified (%s).', self.known.subparser)
            return False

        # Read crendential
        if self.known.dsm_user is None:
            self.known.dsm_user = input('Username: ')
        if self.known.dsm_password is None:
            self.known.dsm_password = getpass.getpass()

        # Record config if enabled
        if self.known.record_config:
            self.process.record_config_details()

        if self.known.subparser == 'list':
            result = list_object(self.known)
        elif self.known.subparser == 'delete_volume':
            result = delete_volume(self.known)
        elif self.known.subparser == 'replace_volume':
            result = replace_volume(self.known)
        elif self.known.subparser == 'clone_volume':
            result = clone_volume(self.known)
        elif self.known.subparser == 'create_snapshot':
            result = create_snapshot(self.known)
        elif self.known.subparser == 'delete_recycled_vols':
            result = delete_recycled_vols(self.known)

        # Record config if enabled
        if self.known.record_config:
            self.process.record_config_details()

        return result


class LoadFromFile(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        with values as f:
            args = json.load(f)

        for k, v in args.items():
            setattr(namespace, k, v)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError('Boolean value expected.')


def list_object(args):
    """
    List Dell SC objects.

    Example: ucamdsm --dsm_user user --dsm_password abc123 list --object scs
    """
    with DSMConnection(args.dsm_host, args.dsm_port, args.dsm_user,
                       args.dsm_password, args.is_secure) as dsm_conn:
        result = None
        dsm_objects = None
        if args.object == 'scs':
            result = dsm_conn.get_scs()
            dsm_objects = dsm_conn.scs
        elif args.object == 'servers':
            result = dsm_conn.get_servers()
            dsm_objects = dsm_conn.servers
        elif args.object == 'volumes':
            result = dsm_conn.get_volumes()
            dsm_objects = dsm_conn.volumes
        elif args.object == 'snapshots':
            result = dsm_conn.get_snapshots()
            dsm_objects = dsm_conn.replays
        elif args.object == 'volFolders':
            result = dsm_conn.get_volume_folders()
            dsm_objects = dsm_conn.volume_folders
        elif args.object == 'snapshotProfiles':
            result = dsm_conn.get_snapshot_profiles()
            dsm_objects = dsm_conn.rply_profiles
        elif args.object == 'recycledVols':
            result = dsm_conn.get_recycled_volumes()
            dsm_objects = dsm_conn.recycled_vols

        if result and dsm_objects is not None:
            if args.output is not None and args.output == 'json':
                LOG.info('List of %s:\n%s',
                         args.object, json.dumps(dsm_objects, indent=4, sort_keys=False))
            else:
                LOG.info('List of %s:\n%s',
                         args.object, '\n'.join(str(item) for item in dsm_objects.items()))

    return result


def delete_volume(args):
    """
    Example: ucamdsm --dsm_user user --dsm_password abc123 delete_volume --vol_wwn 12345
    """
    with Task(args.dsm_host, args.dsm_port, args.dsm_user, args.dsm_password, args.is_secure) as task:
        result = task.delete_volume(args.vol_wwn, recycle=args.recycle)

    if result:
        LOG.info('delete_volume(%s, recycle=%s) succeeded. Result: %s.',
                 args.vol_wwn, args.recycle, result)
    else:
        LOG.error('delete_volume(%s, recycle=%s) failed. Result: %s.',
                  args.vol_wwn, args.recycle, result)

    return result


def replace_volume(args):
    """
    Example: ucamdsm --dsm_user user --dsm_password abc123 replace_volume --src_mp /src --dst_mp /dst
    """
    with Task(args.dsm_host, args.dsm_port, args.dsm_user, args.dsm_password, args.is_secure) as task:
        result = task.replace_volume(args.src_mp, args.dst_mp)

    if result:
        LOG.info('replace_volume(%s, %s) succeeded. Result: %s.', args.src_mp, args.dst_mp, result)
    else:
        LOG.error('replace_volume(%s, %s) failed. Result: %s.', args.src_mp, args.dst_mp, result)

    return result


def clone_volume(args):
    """
    Example: ucamdsm --dsm_user user --dsm_password abc123 clone_volume \
        --vol_wwn 12345 --replay_label test1 \
        --target_mp /target
    """
    with Task(args.dsm_host, args.dsm_port, args.dsm_user, args.dsm_password, args.is_secure) as task:
        result = task.clone_volume(args.vol_wwn, args.replay_label, args.target_mp)

    if result:
        LOG.info('clone_volume(%s, %s, %s) succeeded. Result: %s.',
                 args.vol_wwn, args.replay_label, args.target_mp, result)
    else:
        LOG.error('clone_volume(%s, %s, %s) failed. Result: %s.',
                  args.vol_wwn, args.replay_label, args.target_mp, result)

    return result


def create_snapshot(args):
    """
    Example: ucamdsm --dsm_user user --dsm_password abc123 \
         create_snapshot --mp /mp --replay_label test1 --retention 5
    """
    with Task(args.dsm_host, args.dsm_port, args.dsm_user, args.dsm_password, args.is_secure) as task:
        result = task.create_snapshot(args.mp, args.replay_label, args.retention)

    if result:
        LOG.info('create_snapshot(%s, %s, %s) succeeded. Result: %s.',
                 args.mp, args.replay_label, args.retention, result)
    else:
        LOG.error('create_snapshot(%s, %s, %s) failed. Result: %s.',
                  args.mp, args.replay_label, args.retention, result)

    return result


def delete_recycled_vols(args):
    """
    Example: ucamdsm --dsm_user user --dsm_password abc123 \
         delete_recycled_vols --wwns_file /tmp/recycled_vols_wwns.txt
    """
    with Task(args.dsm_host, args.dsm_port, args.dsm_user, args.dsm_password, args.is_secure) as task:
        result = task.delete_recycled_vols(args.wwns_file)

    if result:
        LOG.info('delete_recycled_vols(%s) succeeded. Result: %s.', args.wwns_file, result)
    else:
        LOG.error('delete_recycled_vols(%s failed. Result: %s.', args.wwns_file, result)

    return result
