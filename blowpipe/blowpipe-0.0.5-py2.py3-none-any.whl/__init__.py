import sys
from blowpipe.client_cli import BlowpipeClient, BlowpipeClientConfig
from blowpipe.server import BlowpipeServer, BlowpipeServerConfig
from blowpipe.utils import CLI
from blowpipe import constants
import blowpipe

from blowpipe.logger import Logger
from blowpipe import bootstrap
import os


def init(cli:CLI):
    """
    initialises the blowpipe.cfg and .db files
    The autodiscover logic will attempt to find in order
    A CLI parameter, the BLOWPIPE_HOME directory or the current directory
    :param cli:
    :return:
    """
    filename = utils.autodiscover_server_config_file("-config", "BLOWPIPE_HOME", "blowpipe.cfg")
    if os.path.isfile(filename):
        # already exists, won't init.
        Logger.console("Error, '" + filename + "' already exists, won't init.")
        sys.exit(1)
    else:
        bootstrap.init(filename)
        return True


def server(cli:CLI):
    filename = utils.autodiscover_server_config_file("-config", "BLOWPIPE_HOME", "blowpipe.cfg")
    if not os.path.isfile(filename):
        msg = "Error, Blowpipe server cannot run, no configuration found." \
            + "\nYou must set one of the following:" \
            + "\n" \
            + "\n\t1. $BLOWPIPE_HOME" \
            + "\n\t2. 'blowpipe.cfg' not found in current dir." \
            + "\n\t3. Pass location of config file with '-config' option." \
            + "\n"
        Logger.console(msg)
        sys.exit(1)

    print("using config" + filename)
    config = BlowpipeServerConfig(filename)
    config.is_repository = cli.contains("-repository")

    if not utils.is_port_available(config.get_grpc_server_ip(), config.get_grpc_port()):
        # looks like something is running on that port.
        # let's see if we can connect to it as the client; if we can
        # then we will be
        if utils.is_server_running(config):
            friendly = config.get_grpc_server_ip() + ":" + str(config.get_grpc_port())
            print("Error, Blowpipe Server is already running on " + friendly)
        else:
            print("Error, port " + str(config.get_grpc_port()) + " already in use by something else.")
        sys.exit(1)
    else:
        utils.print_logo()
        srv = BlowpipeServer(config)
        srv.start(blocking=True)


def client(cli:CLI):
    filename = utils.autodiscover_server_config_file("-config", "BLOWPIPE_HOME", "blowpipe.cfg")
    default_filename = utils.resolve_file("~/.blowpipe/blowpipe.cfg")
    if not os.path.isfile(filename):
        if not os.path.isfile(default_filename):
            Logger.console("No configuration file found.")
            sys.exit(1)
        else:
            filename = default_filename

    config = BlowpipeClientConfig(filename)

    # the client doesn't care! - default to localhost:50051 or BLOWPIPE_SERVER_URL for now
    default_server = config.get_grpc_server_ip() + ":" + str(config.get_grpc_port())
    server_url = os.getenv("BLOWPIPE_URL", default_server)
    splits = server_url.split(":")
    hostname = splits[0]
    port = splits[1]

    config.set_grpc_server_ip(hostname)
    config.set_grpc_port(port)

    cli = utils.CLI()
    client = BlowpipeClient(config)
    client.process(cli)


def main():
    cli = CLI(sys.argv)
    blowpipe.logger.CONSOLE_ENABLED = cli.contains("-v")
    if cli.get_command() == "init":
        init(cli)
    elif cli.get_command() == "server":
        server(cli)
    else:
        client(cli)
