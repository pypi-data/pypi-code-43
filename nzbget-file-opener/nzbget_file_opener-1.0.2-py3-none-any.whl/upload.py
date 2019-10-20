import base64
import os


class AppendOptions:
    """ Stores all the options needed to perform the proxy 'append' method """

    def __init__(self, args):
        self.category = args.category if args.category else ''
        self.priority = args.priority if args.priority else 0
        self.add_top = args.add_top
        self.add_paused = args.add_paused
        self.dupe_key = ''
        self.dupe_score = 0
        self.dupe_mode = 'SCORE'


def get_file_data(filepath):
    """ Returns the raw data of a nzb file """
    with open(filepath, 'rb') as file:
        nzb_content = file.read()
        return base64.standard_b64encode(nzb_content).decode("utf-8")


def upload_file(filepath, proxy, args):
    """ Uploads a file to NZBGet via a XML-RPC server proxy """
    print(f'Treating {filepath.split("/")[-1]}')
    o = AppendOptions(args)
    data = get_file_data(filepath)
    proxy.append(filepath, data, o.category, o.priority, o.add_top, o.add_paused, o.dupe_key, o.dupe_score, o.dupe_mode)
    if args.delete_files:
        os.remove(filepath)

