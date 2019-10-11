import logging
from distutils.core import run_setup

from .package_file import discover_dists
from .exceptions import NoDistFilesFoundError

logger = logging.getLogger()


def upload_package(repository, versions=None, skip_empty_versions=False):
    package = run_setup('setup.py', stop_after='config')
    package_meta = package.metadata
    logging.info(f'Found package %s.', package_meta.get_name())

    if not versions:
        versions = [package_meta.get_version()]

    # for n in dir(package):
    #     val = getattr(package, n)
    #     if n.startswith('get_'):
    #         try:
    #             val = val()
    #         except:
    #             val = getattr(package, n)
    #     print(f"{Fore.GREEN}{n}{Fore.LIGHTGREEN_EX}: {Fore.BLACK}{val}{Style.RESET_ALL}")

    for version in versions:
        logging.info(f'Processing version %s.', version, extra={'indent': 1})
        package_meta.version = version
        try:
            repository.upload_files(package_meta.get_name(), list(discover_dists(package_meta)))
        except NoDistFilesFoundError as e:
            if skip_empty_versions:
                logger.warning(f'{e.args[0]} Skipping...', *e.args[1:])
            else:
                raise
