import os
import subprocess

# TODO: proper automatic dev/release versioning
# Notes:
#   - A release should be tagged:
#       $ git tag -a v0.1 -m "Initial public release" master
#       $ git push --tags
#       see https://www.atlassian.com/git/tutorials/comparing-workflows#gitflow-workflow
#   - https://github.com/tqdm/tqdm/blob/master/CONTRIBUTING.md#merging-pull-requests
# Useful commands:
#   - branch name: $ git rev-parse --abbrev-ref HEAD
#   - last tag (only if tag with annotation): $ git describe
#   - it no annotated tag: $ git describe --always


def get_git_revision(path: str) -> str:
    """
    Returns the git revision as a string
    """
    git_revision = 'unknown'
    if os.path.exists(path):
        try:
            git_revision = subprocess.check_output(
                ["git", "describe", "--always"]
            ).strip().decode('ascii')

        except subprocess.CalledProcessError:
            pass

    return git_revision


def get_git_revision_extra(path: str) -> str:
    git_revision = get_git_revision(path=path)
    return '-dev0+' + git_revision[:7]


# def get_version_info(version, is_release):
#     full_version = version
#     git_revision = get_git_revision()
#
#     if not is_release:
#         full_version += '.dev0+' + git_revision[:7]
#
#     return full_version, git_revision
#
# def write_version_py(filename, version, is_release):
#     content = """
# # THIS FILE IS GENERATED FROM SETUP.PY
#
# short_version = '{version}'
# version = '{version}'
# full_version = '{full_version}'
# git_revision = '{git_revision}'
# is_release = {is_release}
#
# if not is_release:
#     version = full_version
# """
#     full_version, git_revision = get_version_info(version, is_release)
#
#     with open(filename, 'w') as file:
#         file.write(content.format(filename=filename,
#                                   version=version,
#                                   full_version=full_version,
#                                   git_revision=git_revision,
#                                   is_release=str(is_release)))
