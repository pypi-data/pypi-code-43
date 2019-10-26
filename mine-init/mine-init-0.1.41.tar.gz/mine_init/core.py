"""
| Main Classes for mine-init
"""
import argparse
import os
import sys
import datetime
import getpass
import socket
import logging
from .utils import PropertyFileManager, MOTDGenerator, PackFileUpdater, PackManager, \
    BufferingSMTPHandler, MakeFileHandler, JavaRunner


DIST = os.getenv('DIST', '/dist')
CACHE = os.getenv('CACHE', '/tmp/packmaker')
SERVER_DIR = os.getenv('SERVER_DIR', '/server')
PROP_FILE = os.getenv('SERVER_PROPERTIES', '/server/server.properties')
MOTD_GEN = MOTDGenerator()
SERVER_PROPS = {
    'motd': MOTD_GEN.generate(),
    'server-port': os.getenv('SERVER_PORT', '25565'),
    'allow-nether': os.getenv('ALLOW_NETHER', 'true'),
    'announce-player-achievements': os.getenv('ANNOUNCE_PLAYER_ACHIEVEMENTS', 'true'),
    'enable-command-block': os.getenv('ENABLE_COMMAND_BLOCK', 'false'),
    'spawn-animals': os.getenv('SPAWN_ANIMALS', 'true'),
    'spawn-monsters': os.getenv('SPAWN_MONSTERS', 'true'),
    'spawn-npcs': os.getenv('SPAWN_NPCS', 'true'),
    'generate-structures': os.getenv('GENERATE_STRUCTURES', 'true'),
    'view-distance': os.getenv('VIEW_DISTANCE', '10'),
    'hardcore': os.getenv('HARDCORE', 'false'),
    'max-build-height': os.getenv('MAX_BUILD_HEIGHT', '256'),
    'force-gamemode': os.getenv('FORCE_GAMEMODE', 'false'),
    'hardmax-tick-timecore': os.getenv('MAX_TICK_TIME', '-1'),
    'enable-query': os.getenv('ENABLE_QUERY', 'false'),
    'query.port': os.getenv('QUERY_PORT', '25565'),
    'enable-rcon': os.getenv('ENABLE_RCON', 'true'),
    'rcon.password': os.getenv('RCON_PASSWORD', 'minecraft'),
    'rcon.port': os.getenv('RCON_PORT', '25575'),
    'max-players': os.getenv('MAX_PLAYERS', '40'),
    'max-world-size': os.getenv('MAX_WORLD_SIZE', '5000'),
    'level-name': os.getenv('LEVEL', 'world'),
    'level-seed': os.getenv('SEED', ''),
    'pvp': os.getenv('PVP', 'true'),
    'generator-settings': os.getenv('GENERATOR_SETTINGS', ''),
    'online-mode': os.getenv('ONLINE_MODE', 'true'),
    'allow-flight': os.getenv('ALLOW_FLIGHT', 'true'),
    'level-type': os.getenv('LEVEL_TYPE'.upper(), 'DEFAULT'),
    'white-list': os.getenv('WHITELIST', 'false'),
    'whitelist': os.getenv('WHITELIST', 'false'),
    'spawn-protection': os.getenv('SPAWN_PROTECTION', '0'),
    'difficulty': os.getenv('DIFFICULTY', '1'),
    'gamemode': os.getenv('GAMEMODE', '0')
}


class MineInit:
    """
    | The main class for the mine-init executable.
    """

    def __init__(self):
        self.hostname = socket.getfqdn()
        self.parser = self.build_parser()
        self.ppid = os.getppid()
        args = self.get_args()
        try:
            func = args.func
        except AttributeError:
            self.parser.error('Too few arguments, see "mine-init -h"')
        self.logger = self.setup_logging(args)
        func(args)

    def setup_logging(self, args):
        """
        | Setup logging
        | :return: logging.Logger instance
        """
        log_dir = args.log_dir
        log_filename = datetime.datetime.now().strftime('%Y-%m-%d') + '.log'
        logger = logging.getLogger('mine-init')
        logger.setLevel(args.log_level)
        log_format = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

        file_handler = MakeFileHandler(filename=os.path.join(log_dir, log_filename))
        file_handler.setLevel(args.log_level)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(args.log_level)
        stream_handler.setFormatter(log_format)
        logger.addHandler(stream_handler)

        self.smtp_handler = BufferingSMTPHandler(
            args.mail_server,
            args.mail_port,
            args.src_email,
            args.dest_email,
            1000
        )
        self.smtp_handler.setLevel(args.log_level)
        self.smtp_handler.setFormatter(log_format)
        logger.addHandler(self.smtp_handler)

        return logger

    def get_args(self):
        """
        | Return parsed arguments object.
        | :return: `object` argparser parsed arguments.
        """
        return self.parser.parse_args()

    def build_parser(self):
        """
        | Build the main argparser for the application and return as an object.
        | :return: `object` argparser
        """
        parser = argparse.ArgumentParser(prog='mine-init')
        subparsers = parser.add_subparsers(dest='subcommands')
        parser.add_argument(
            '-v', '--verbose',
            dest='verbose',
            action='store_true',
            help='Make things chatty.'
        )

        parser.add_argument(
            '--dest-email',
            dest='dest_email',
            type=str,
            default='root@localhost',
            help='The email address to send the backup report to. Defaults to root@localhost.'
        )

        parser.add_argument(
            '--source-email',
            dest='src_email',
            type=str,
            default="%s@%s" % (getpass.getuser(), socket.getfqdn()),
            help='(optional) The email address to send the backup report from. Defaults to '
                 '%s@%s' % (getpass.getuser(), socket.getfqdn())
        )

        parser.add_argument(
            '--mail-server',
            dest='mail_server',
            type=str,
            default='localhost',
            help='(optional) The mail server to use to send mail. Defaults to localhost.'
        )

        parser.add_argument(
            '--mail-port',
            dest='mail_port',
            type=int,
            default=25,
            help='(optional) The port on which to connect to the mail server. Defaults to 25.'
        )

        parser.add_argument(
            '--log-level',
            dest='log_level',
            type=str,
            default='INFO',
            help='(optional) The logging level, defaults to INFO.'
        )

        parser.add_argument(
            '--log-dir',
            dest='log_dir',
            type=str,
            default='/server/mine-init/logs',
            help='(optional) The directory to place logs. Defaults to /server/mine-init/logs'
        )

        parser_start = subparsers.add_parser(
            'start',
            help='Starts and monitors a Minecraft instance.'
        )
        parser_start.add_argument(
            '-x', '--no-update',
            action='store_true',
            dest='update',
            help='Disable update of the server directory from the distribution directory.'
                 ' Defaults to false.'
        )
        parser_start.add_argument(
            '-d', '--dist', '--distribution-dir',
            dest='dist',
            default=[DIST],
            action='append',
            help='The directory containing the distribution files, like default server.properties,'
                 ' configs, and as infrequently as possible (to prevent bloat and legal issues)'
                 ' mods. Defaults to "/dist". To tell packmaker to merge multiple directories, pass'
                 ' this argument multiple times.'
        )
        parser_start.add_argument(
            '-s', '--server', '--server-dir',
            type=str,
            dest='server',
            default=SERVER_DIR,
            help='The directory where the server root will be (or is). Defaults to "/server".'
        )
        parser_start.add_argument(
            '-c', '--cache', '--cache-dir',
            type=str,
            dest='cache',
            default=CACHE,
            help='The directory containing cached files, often files downloaded by the'
                 ' pack manager process. The cache is used to speed up subsequent server starts'
                 ' so that these files do not need to be downloaded on every start.'
                 ' Defaults to "/tmp/packmaker".'
        )
        parser_start.set_defaults(func=self.start)
        return parser

    def start(self, args):
        """
        | Starts and updates a Minecraft instance.
        | :param args: `object` argparse arguments object.
        | :return:
        """

        self.logger.info('Initializing start routine...')
        pack_manager = PackManager(args.dist, args.cache)
        pack_update = PackFileUpdater(args.dist[0], args.server)
        prop_manager = PropertyFileManager(PROP_FILE, SERVER_PROPS)

        self.logger.info('Syncing pack files to server directory and updating settings...')
        pack_manager.install_pack()
        pack_update.sync()
        prop_manager.read()
        prop_manager.update_properties()
        prop_manager.write()

        self.logger.info('Prepare for launch...')
        server = JavaRunner(args.server, args.dist)
        server.main()

        sys.exit(0)
