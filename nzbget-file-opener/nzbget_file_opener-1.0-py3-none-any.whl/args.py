import argparse
import os


def check_file(extensions: [str] = None):
    class FileChecker(argparse.Action):
        def __call__(self, parser, namespace, files, option_string=None):
            to_check = files
            if not isinstance(to_check, list):
                to_check = [to_check]
            for file in to_check:
                if not os.path.exists(file):
                    parser.error(f'file \'{file}\' does not exists')
                if not extensions:
                    continue
                ext = file.split('.')[-1]
                if ext not in extensions:
                    parser.error(f'file extension \'{ext}\' not allowed. Choices are \'{", ".join(extensions)}\'')
            setattr(namespace, self.dest, files)
    return FileChecker


def get_arguments(custom_args=None):
    """ Returns an argparse object generated from the command line arguments given """
    parser = argparse.ArgumentParser(description='Process app input arguments')

    # Host
    parser.add_argument('-n', '--hostname', type=str,
                        dest='hostname',
                        help="the nzbget hostname to reach")
    parser.add_argument('-u', '--username', type=str,
                        dest='username',
                        help="your nzbget username")
    parser.add_argument('-p', '--password', type=str,
                        dest='password',
                        help="your nzbget password")

    # File config
    parser.add_argument('-l', '--load-config', type=str,
                        action=check_file(), dest='config',
                        help="your nzbget config")
    parser.add_argument('-d', '--domain', type=str,
                        dest='domain',
                        help="the domain target defined in your nzbget config")

    # NZB Meta
    parser.add_argument('-c', '--category', type=str,
                        dest='category',
                        help="the category to use for the nzb files download")
    parser.add_argument('-P', '--priority', type=str,
                        dest='priority',
                        help="the category to use for the nzb files download")

    # Queue options
    parser.add_argument('--add-top',
                        action='store_true', dest='add_top',
                        help="add the files to the top of queue")
    parser.add_argument('--add-paused',
                        action='store_true', dest='add_paused',
                        help="add the files in pause state")

    # Local link to app
    parser.add_argument('--app-path', type=str,
                        dest='nzbget_path',
                        help="specify the nzbget app path to launch it if not already running")

    # NZBs
    parser.add_argument('-D', '--delete-files',
                        action='store_true', dest='delete_files',
                        help="to delete the files sent to NZBget")
    parser.add_argument('files', nargs='+',
                        action=check_file(['nzb']),
                        help="the files to send")

    args = parser.parse_args(args=custom_args)

    if args.config and (args.username or args.password):
        parser.error('cannot use config file along with credentials')
    if args.domain and not args.config:
        parser.error('cannot use domain without config file')
    if args.config and args.hostname:
        parser.error('cannot use config file along with hostname. please use -d option instead')
    if (args.username and not args.password) or (args.password and not args.username):
        parser.error('-u and -p options are inclusive')
    return args
