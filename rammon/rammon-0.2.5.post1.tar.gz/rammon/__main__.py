import argparse
from rammon.commands import start, stop, status, enable, disable, config


def main():
    parser = argparse.ArgumentParser(
        description="Notifies you when low on memory",
        add_help=False,
        usage="""rammon [-h | --help] [-d | --no-daemon] [--set OPTION=value] [command]

    Commands are:
       start      Start the memory monitor
       stop       Stop the memory monitor
       status     Check the status of the memory monitor
       enable     Set rammon to run on login as a systemd user service
       disable    Disable rammon's auto-start
       config     Get and set configuration options

    Check command options with:
       rammon <command> -h
    """,
    )
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-d", "--no-daemon", action="store_false", dest="daemon")
    parser.add_argument("--set", action="append", dest="settings")
    parser.add_argument(
        "command",
        default="start",
        choices=["start", "stop", "status", "enable", "disable", "config"],
        nargs="?",
    )
    args = parser.parse_args()
    if args.help:
        print(parser.usage)
        return
    # TODO: Workout a more elegant of passing through the arguments
    {
        "start": start,
        "stop": stop,
        "status": status,
        "enable": enable,
        "disable": disable,
        "config": config,
    }[args.command](**dict(args._get_kwargs()))


if __name__ == "__main__":
    main()
