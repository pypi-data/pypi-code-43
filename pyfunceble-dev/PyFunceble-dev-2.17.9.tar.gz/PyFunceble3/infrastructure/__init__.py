from os import path
from os import sep as directory_separator

from box import Box

import PyFunceble3.abstracts as abstracts
import PyFunceble3.helpers as helpers


def get_output_parent_directory():
    """
    Provides the parent location of the output directory.
    """

    return helpers.Directory.get_current(with_end_sep=True)


def get_config_directory():
    """
    Provides the base location config directory.
    """

    # pylint: disable=too-many-branches,too-many-return-statements

    pyfunceble_config_dir = abstracts.Environments.is_present(
        "PYFUNCEBLE_CONFIG_DIR", return_value=True
    )
    pyfunceble_output_dir = abstracts.Environments.is_present(
        "PYFUNCEBLE_OUTPUT_DIR", return_value=True
    )
    travis_build_dir = abstracts.Environments.is_present(
        "TRAVIS_BUILD_DIR", return_value=True
    )

    if pyfunceble_config_dir:
        if not pyfunceble_config_dir.endswith(directory_separator):
            return pyfunceble_config_dir + directory_separator
        return pyfunceble_config_dir
    if pyfunceble_output_dir:
        if not pyfunceble_output_dir.endswith(directory_separator):
            return pyfunceble_output_dir + directory_separator
        return pyfunceble_output_dir
    if abstracts.Version.is_cloned():
        return helpers.Directory.get_current(with_end_sep=True)
    if travis_build_dir:
        if not travis_build_dir.endswith(directory_separator):
            return travis_build_dir + directory_separator
        return travis_build_dir

    if abstracts.Platform().is_unix():
        home_dir = path.expanduser("~") + directory_separator
        dir_path = (
            f"{home_dir}.config{directory_separator}"
            f"{abstracts.Package.NAME}{directory_separator}"
        )

        if helpers.Directory(dir_path=dir_path).exists():
            return dir_path
        if helpers.Directory(home_dir).exists():
            return f"{home_dir}.{abstracts.Package.NAME}{directory_separator}"
        return helpers.Directory.get_current(with_end_sep=True)

    if abstracts.Platform().is_windows():
        app_data_dir = abstracts.Environments.is_present("APPDATA", return_value=True)

        if app_data_dir:
            app_data_dir += f"{abstracts.Package.NAME}{directory_separator}"

            if not app_data_dir.endswith(directory_separator):
                return app_data_dir + directory_separator
            return app_data_dir + directory_separator

    return helpers.Directory.get_current(with_end_sep=True)
