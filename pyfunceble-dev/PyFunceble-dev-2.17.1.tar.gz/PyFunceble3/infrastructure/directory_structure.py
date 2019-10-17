from os import walk

from .logger import Logger
import PyFunceble3.helpers as helpers
import PyFunceble3.converters as converters


class DirectoryStructure:
    def __init__(self, configuration, output_parent_directory, production=False):
        self.config = configuration
        self.logger = Logger(self.config)

        self.output_directory_parent = output_parent_directory
        self.internal_file = (
            self.output_directory_parent
            + self.config.outputs.default_files.dir_structure
        )

    def backup(self):
        """
        Backups the developer state of `output/` in order to make it restorable
        and portable for user.
        """

        self.logger.info(f"Backing up the directory structure..")

        # We initiate the structure base.
        result = {self.config.outputs.parent_directory: {}}

        for root, _, files in walk(self.output_directory):
            # We loop through the current output directory structure.

            # We get the currently read directory name.
            directories = helpers.Directory(
                root.split(self.output_directory)[1]
            ).fix_path()

            # We initiate a local variable which will get the structure of the subdirectory.
            local_result = result[self.config.outputs.parent_directory]

            for file in files:
                # We loop through the list of files.

                # We construct the file path.
                file_path = root + self.directory_separator + file

                # We get the hash of the file.
                file_hash = helpers.Hash().file(file_path)

                # We convert the file content to a list.
                lines_in_list = [line.rstrip("\n") for line in open(file_path)]

                # We convert the file content into a more flat format.
                # We use `@@@` as glue and implicitly replacement for `\n`.
                formatted_content = "@@@".join(lines_in_list)

                # We update the local result (and implicitly the global result)
                # with the files and directory informations/structure.
                local_result = local_result.setdefault(
                    directories,
                    {file: {"sha512_254": file_hash, "content": formatted_content}},
                )

                self.logger.info(f"{file_path} backed up.")

        # We finally save the directory structure into the production file.
        helpers.Dict(result).to_json(
            self.output_directory_parent + "dir_structure_production.json"
        )

        self.logger.info(f"Backup saved into dir_structure_production.json")

    def update_from_config(self, structure):
        """
        Updates the structure based on the configuration setting.
        """

        base_map = {"output/": self.config.outputs.parent_directory}

        replace_map = {
            #########################################################################
            #            The following part is there for historical reason.         #
            #########################################################################
            # We get the replacement of the HTTP_Analytic directory from the
            # configuration file.
            "HTTP_Analytic/": self.config.outputs.analytic.directories.parent,
            # We get the replacement of the HTTP_Analytic/ACTIVE directory from the
            # configuration file.
            "HTTP_Analytic/ACTIVE/": self.config.outputs.analytic.directories.parent
            + self.config.outputs.analytic.directories.up,
            "HTTP_Analytic/POTENTIALLY_ACTIVE/": self.config.outputs.analytic.directories.parent
            + self.config.outputs.analytic.directories.potentially_up,
            # We get the replacement of the HTTP_Analytic/POTENTIALLY_INACTIVE directory
            # from the configuration file.
            "HTTP_Analytic/POTENTIALLY_INACTIVE/": self.config.outputs.analytic.directories.parent
            + self.config.outputs.analytic.directories.potentially_down,
            #########################################################################
            #             The previous part is there for historical reason.         #
            #########################################################################
            # We get the replacement of the Analytic directory from the
            # configuration file.
            "Analytic/": self.config.outputs.analytic.directories.parent,
            # We get the replacement of the Analytic/ACTIVE directory from the
            # configuration file.
            "Analytic/ACTIVE/": self.config.outputs.analytic.directories.parent
            + self.config.outputs.analytic.directories.up,
            "Analytic/POTENTIALLY_ACTIVE/": self.config.outputs.analytic.directories.parent
            + self.config.outputs.analytic.directories.potentially_up,
            # We get the replacement of the Analytic/POTENTIALLY_INACTIVE directory
            # from the configuration file.
            "Analytic/POTENTIALLY_INACTIVE/": self.config.outputs.analytic.directories.parent
            + self.config.outputs.analytic.directories.potentially_down,
            # We get the replacement of the Analytic/SUSPICIOUS directory
            # from the configuration file.
            "Analytic/SUSPICIOUS/": self.config.outputs.analytic.directories.parent
            + self.config.outputs.analytic.directories.suspicious,
            # We get the replacement of the complements directory from the
            # configuration file.
            "complements/": self.config.outputs.complements.directory,
            # We get the replacement of the complements/ACTIVE directory from the
            # configuration file.
            "complements/ACTIVE/": self.config.outputs.complements.directory
            + self.config.status.official.up,
            # We get the replacement of the complements/INACTIVE directory from the
            # configuration file.
            "complements/INACTIVE/": self.config.outputs.complements.directory
            + self.config.status.official.down,
            # We get the replacement of the complements/INVALID directory from the
            # configuration file.
            "complements/INVALID/": self.config.outputs.complements.directory
            + self.config.status.official.invalid,
            # We get the replacement of the complements/VALID directory from the
            # configuration file.
            "complements/VALID/": self.config.outputs.complements.directory
            + self.config.status.official.valid,
            # We get the replacement of the domains directory from the
            # configuration file.
            "domains/": self.config.outputs.domains.directory,
            # We get the replacement of the domains/ACTIVE directory from the
            # configuration file.
            "domains/ACTIVE/": self.config.outputs.domains.directory
            + self.config.status.official.up,
            # We get the replacement of the domains/INACTIVE directory from the
            # configuration file.
            "domains/INACTIVE/": self.config.outputs.domains.directory
            + self.config.status.official.down,
            # We get the replacement of the domains/INVALID directory from the
            # configuration file.
            "domains/INVALID/": self.config.outputs.domains.directory
            + self.config.status.official.invalid,
            # We get the replacement of the domains/VALID directory from the
            # configuration file.
            "domains/VALID/": self.config.outputs.domains.directory
            + self.config.status.official.valid,
            # We get the replacement of the hosts directory from the
            # configuration file.
            "hosts/": self.config.outputs.hosts.directory,
            # We get the replacement of the hosts/ACTIVE directory from the
            # configuration file.
            "hosts/ACTIVE/": self.config.outputs.hosts.directory
            + self.config.status.official.up,
            # We get the replacement of the hosts/INACTIVE directory from the
            # configuration file.
            "hosts/INACTIVE/": self.config.outputs.hosts.directory
            + self.config.status.official.down,
            # We get the replacement of the hosts/INVALID directory from the
            # configuration file.
            "hosts/INVALID/": self.config.outputs.hosts.directory
            + self.config.status.official.invalid,
            # We get the replacement of the hosts/VALID directory from the
            # configuration file.
            "hosts/VALID/": self.config.outputs.hosts.directory
            + self.config.status.official.valid,
            # We get the replacement of the json directory from the
            # configuration file.
            "json/": self.config.outputs.json.directory,
            # We get the replacement of the json/ACTIVE directory from the
            # configuration file.
            "json/ACTIVE/": self.config.outputs.json.directory
            + self.config.status.official.up,
            # We get the replacement of the json/INACTIVE directory from the
            # configuration file.
            "json/INACTIVE/": self.config.outputs.json.directory
            + self.config.status.official.down,
            # We get the replacement of the json/INVALID directory from the
            # configuration file.
            "json/INVALID/": self.config.outputs.json.directory
            + self.config.status.official.invalid,
            # We get the replacement of the json/VALID directory from the
            # configuration file.
            "json/VALID/": self.config.outputs.json.directory
            + self.config.status.official.valid,
            # We get the replacement of the logs directory from the
            # configuration file.
            "logs/": self.config.outputs.logs.directories.parent,
            # We get the replacement of the logs/percentage directory from the
            # configuration file.
            "logs/percentage/": self.config.outputs.logs.directories.parent
            + self.config.outputs.logs.directories.percentage,
            # We get the replacement of the splited directory from the
            # configuration file.
            "splited/": self.config.outputs.splited.directory,
        }

        replaced = {}

        for mapped, declared in replace_map.items():
            declared = helpers.Directory(declared).fix_path()
            replaced.update({mapped: declared})

        base_replaced = {}

        for mapped, declared in base_map.items():
            declared = helpers.Directory(declared).fix_path()
            base_replaced.update({mapped: declared})

        structure = helpers.Dict(structure).rename_key(base_replaced)
        structure[self.config.outputs.parent_directory] = shelpers.Dict(
            structure(structure[self.config.outputs.parent_directory])
        ).rename_key(replaced)

        try:
            helpers.Dict(structure).to_json_file(self.internal_file)
        except FileNotFoundError:
            self.helpers.helpers.Directory(
                self.directory_separator.join(
                    self.internal_file.split(self.directory_separator)[:-1]
                )
            ).create()

            self.helpers.helpers.Dict(structure).to_json_file(self.internal_file)

    def get_structure(self):
        """
        Provides the structure to reconstruct.
        """

        structure_file = None
        req = None

        if helpers.File(self.internal_file).exists():
            structure_file = self.internal_file
        elif helpers.File(self.output_directory_parent + "dir_structure_production.json").exists():
            structure_file = self.output_directory_parent + "dir_structure_production.json"
        else:
            req = 0