# pylint: disable=import-error
from box import Box

import PyFunceble3.abstracts as abstracts
import PyFunceble3.converters as converters
import PyFunceble3.exceptions as exceptions
import PyFunceble3.helpers as helpers

from .directory_structure import DirectoryStructure


class LoadConfig:
    def __init__(self, config_dir_path):
        config_dir_path = helpers.Directory(config_dir_path).fix_path()

        self.data = Box(
            {"config": {}, "intern": {}}, default_box=True, default_box_attr=None
        )
        self.config_location, self.default_config_location = self.get_possible_config_file_path(
            config_dir_path
        )

        self.__load_it()
        self.fix_main_paths()

    @classmethod
    def get_possible_config_file_path(cls, config_dir_path):
        """
        Given a directory where we should find the configuration file,
        we produce a tuple with 2 possible files:

            1. .PyFunceble.yaml
            2 /path/to/.PyFunceble_production.yaml

        .. note::
            This method never check if they exists.

        :param str config_dir_path: The path of a directory to look into.
        """

        return (
            f"{config_dir_path}{abstracts.Infrastructure.CONFIGURATION_FILENAME}",
            f"{config_dir_path}{abstracts.Infrastructure.DEFAULT_CONFIGURATION_FILENAME}",
        )

    def fix_main_paths(self):
        """
        Fix all main paths.
        """

        for main_key in [
            "domains",
            "hosts",
            "splited",
            "json",
            "complements",
            "db_type",
        ]:
            try:
                self.data.config.outputs[main_key].directory = helpers.Directory(
                    self.data.config.outputs[main_key].directory
                ).fix_path()
            except KeyError:
                pass

        for main_key in ["analytic", "logs"]:
            for key, value in self.data.config.outputs[main_key].directories.items():
                self.data.config.outputs[main_key].directories[key] = helpers.Directory(
                    value
                ).fix_path()

        self.data.config.outputs.parent_directory = helpers.Directory(
            self.data.config.outputs.parent_directory
        ).fix_path()

    def __ask_user_authorization_to_install_it(self):
        if "PyFunceble3" in __name__:
            cli_text = abstracts.CLIText()
            while True:
                response = input(
                    abstracts.Messages.get("install_config", "en")
                    % {
                        "not_found_path": f"{cli_text.styles.BRIGHT}"
                        f"{self.config_location}{cli_text.styles.RESET_ALL}"
                    }
                )

                if isinstance(response, str):
                    if response.lower()[0] in abstracts.Messages.YES_VALUES:
                        self.install_production_config()
                        break
                    if response.lower()[0] in abstracts.Messages.NO_VALUES:
                        raise exceptions.ConfigurationFileNotFound(self.config_location)
        else:
            self.install_production_config()

        self.load_configuration_file()

    def __load_it(self):
        try:
            self.load_configuration_file()
        except exceptions.ConfigurationFileNotFound:
            if not abstracts.Environments.is_present("PYFUNCEBLE_AUTO_CONFIGURATION"):
                self.__ask_user_authorization_to_install_it()

    def load_configuration_file(self):
        try:
            self.data.config.update(helpers.Dict.from_yaml_file(self.config_location))
        except FileNotFoundError:
            default_config_location_file_instance = helpers.File(
                self.default_config_location
            )

            if default_config_location_file_instance.exists():
                default_config_location_file_instance.copy(self.config_location)

                self.load_configuration_file()
            else:
                raise exceptions.ConfigurationFileNotFound(self.config_location)

    def install_production_config(self):
        if not abstracts.Version.is_cloned():
            # pylint: disable=line-too-long
            production_config_link = "https://raw.githubusercontent.com/funilrys/PyFunceble/dev/.PyFunceble_production.yaml"
            production_config_link = converters.InternalUrl(
                production_config_link
            ).to_right_version()

            helpers.Download(production_config_link).text(
                destination=self.default_config_location
            )
