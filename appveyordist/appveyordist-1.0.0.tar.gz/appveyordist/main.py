"""Library routines for pulling from appveyor"""
from . import appvapi
import argparse, os, logging, requests, configparser
log = logging.getLogger(__name__)

CONFIG_FILE = 'appveyordist.conf'

def download_to_directory(username,project,directory,overwrite=False):
    session = requests.Session()
    for base,url in appvapi.latest_build_artifacts(username,project):
        final = os.path.join(directory,base)
        if overwrite or not os.path.exists(final):
            response = requests.get(url)
            response.raise_for_status()
            log.warning('Downloading %s', base)
            with open(final+'~','wb') as fh:
                for chunk in response.iter_content(chunk_size=256000):
                    fh.write(chunk)
            os.rename(final+'~', final)
        else:
            log.info('Skipping %s (already exists)', base)

def get_options():
    defaults = load_defaults()
    parser = argparse.ArgumentParser(
        description='Pull latest build artefacts from appveyor',
    )
    parser.add_argument(
        '-u','--user',help='Appveyor username for the project (default to ./appveyordist.conf user setting)',
        default = defaults.get('user'),
    )
    parser.add_argument(
        '-p','--project',help='Appveyor project name (default to ./appveyordist.conf project setting)',
        default =  defaults.get('project'),
    )
    parser.add_argument(
        '-f','--force',help='If specified, overwrite existing files in destination',
        default=False,
        action='store_true',
    )
    parser.add_argument(
        '-d','--dist',help='Directory into which to store the downloaded files',
        default='dist',
    )
    return parser

def load_defaults():
    if os.path.exists(CONFIG_FILE):
        parser = configparser.ConfigParser()
        parser.read(CONFIG_FILE)
        return {
            'user': parser.get('DEFAULT','user'),
            'project': parser.get('DEFAULT','project'),
        }
    return {}

def main():
    logging.basicConfig(level=logging.INFO)
    parser = get_options()
    options = parser.parse_args()
    if not options.user:
        parser.error("You must provide your appveyor user with -u")
    if not options.project:
        parser.error("You must provide your appveyor project with -p")
    download_to_directory(
        options.user,
        options.project,
        directory=options.dist,
        overwrite=options.force,
    )
