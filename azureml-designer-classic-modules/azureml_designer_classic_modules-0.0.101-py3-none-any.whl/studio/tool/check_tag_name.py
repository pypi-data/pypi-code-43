import argparse

from azureml.studio.package_info import __version__
from azureml.studio.common.version import Version
from azureml.studio.core.utils.strutils import remove_prefix


def check_tag_name(tag_name, prefix='alghost_'):
    if not tag_name:
        raise ValueError(f"tag_name must not be empty.")

    if not tag_name.startswith(prefix):
        raise ValueError(f"Bad tag_name '{tag_name}': Must starts with {prefix}.")

    version_str = remove_prefix(tag_name, prefix=prefix)

    version = Version.parse(__version__)

    if not Version.parse(version_str) == version:
        raise ValueError(f"Bad tag name '{tag_name}': Supposed to be '{prefix}{version.version_str}'.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        "Tag name checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""A CLI tool to check if the given tag name is match the current alghost version.

Example Usage:

python check_tag_name.py --tag-name=alghost_0.0.50
    Will raise error if current version is not 0.0.50. Otherwise do nothing.

"""
    )

    parser.add_argument(
        '--tag-name', type=str,
        help="Tag name to be checked."
    )

    parser.add_argument(
        '--prefix', type=str, default='alghost_',
        help="Tag name prefix."
    )

    args = parser.parse_args()
    check_tag_name(args.tag_name, args.prefix)
