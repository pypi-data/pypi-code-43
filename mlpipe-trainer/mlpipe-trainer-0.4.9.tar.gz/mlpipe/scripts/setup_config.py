"""
Util to setup the config.ini file
Fills the API url and the job token of a specific config.ini file
"""
import configparser
from argparse import ArgumentParser


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--path", dest="path", help="path to config file", required=True)
    parser.add_argument("-u", "--url", dest="url", help="URL of API", required=True)
    parser.add_argument("-t", "--token", dest="job_token", help="Job Token", required=True)
    args = parser.parse_args()

    cp = configparser.ConfigParser()
    if len(cp.read(args.path)) == 0:
        raise ValueError("Config file not found for path: " + args.path)

    cp.set('api_manager', 'job_token', args.job_token)
    cp.set('api_manager', 'url', args.url)
    with open(args.path, 'w') as configfile:
        cp.write(configfile)
