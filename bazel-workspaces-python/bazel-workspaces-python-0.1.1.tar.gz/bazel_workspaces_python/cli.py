r"""Module which is used as the bazel-workspaces-python console script.

Example:
    Example usage of bazel-workspaces-python to generate a Bazel workspace for
    markupsafe package is::

        $ bazel-workspaces-python markupsafe

    Which generates the Bazel workspace for markupsafe in
    `~/bazel_py_modules/markupsafe`, where `~/bazel_py_modules` is a default
    directory for storing workspaces.

    That directory can be changed by the command line argument::

        $ bazel-workspaces-python --main-directory ~/my_py_workspaces

    Or by the environment variable `BAZEL_W_P_MAIN_DIRECTORY`::

        $ export BAZEL_W_P_MAIN_DIRECTORY=$HOME/my_py_workspace
        $ bazel-workspaces-python markupsafe

    The main goal of bazel-workspaces-python is to build projects using Bazel
    using Python dependencies installed in system, not from pip or as bundled
    tarballs. For that purpose, an example of using bazel-workspaces-python in
    rpmspec is::

        %prep
        [...]
        export BAZEL_W_P_MAIN_DIRECTORY=%{_sourcedir}/repos
        bazel-workspaces-python markupsafe
        [...]

        %build
        bazel build \
            --override_repository="markupsafe=%{_sourcedir}/repos/markupsafe" \
            //...

    In future we might provide a set of macros for building Bazel projects
    which will be built on top of bazel-workspaces-python and hide explicit
    usage of bazel-workspace-python and `--override_repository` argument from
    packagers.

Attributes:
    DEFAULT_MAIN_DIR (string): Default main path to create Bazel workspaces in.

"""

import argparse
import os

from bazel_workspaces_python import sources, template

DEFAULT_MAIN_DIR = os.path.expanduser("~/bazel_py_modules")


def main():
    """Create an argument parser and execute as console script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-directory", action="store", type=str,
                        default=os.environ.get("BAZEL_W_P_MAIN_DIRECTORY",
                                               DEFAULT_MAIN_DIR),
                        dest="main_directory",
                        help="Main directory in which workspaces are "
                        "generated")
    parser.add_argument("python_module",
                        help="Python module to generate a Bazel workspace for")
    args = parser.parse_args()

    module_sources = sources.get_module_sources(args.python_module)
    build_content = template.generate_build_template(args.python_module,
                                                     module_sources)
    workspace_content = template.generate_workspace_template(
        args.python_module)

    os.makedirs(os.path.join(args.main_directory, args.python_module),
                exist_ok=True)
    with open(
            os.path.join(args.main_directory, args.python_module, "BUILD"), "w"
    ) as f_build:
        f_build.write(build_content)
    with open(
            os.path.join(args.main_directory, args.python_module, "WORKSPACE"),
            "w"
    ) as f_workspace:
        f_workspace.write(workspace_content)
    print("Repository succesfully generated")
