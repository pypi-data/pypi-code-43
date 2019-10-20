from xmlrpc.client import ServerProxy

from nzbget_file_opener.args import get_arguments
from nzbget_file_opener.config import AppConfig
from nzbget_file_opener.nzbget import detect_nzbget_app
from nzbget_file_opener.upload import upload_file


def main():
    """ Application entry point """
    args = get_arguments()
    config = AppConfig()
    config.load(args)
    detect_nzbget_app(config.hostname, args.nzbget_path)
    print(f'Connecting to {config.url} via xmlrpc')
    proxy = ServerProxy(f'{config.url}/xmlrpc')
    try:
        for entry in args.files:
            upload_file(entry, proxy, args)
    except ConnectionRefusedError:
        print(f'Cannot reach host \'{config.host}\'. Verify that the application is running and accessible')
        exit(1)


if __name__ == '__main__':
    main()
