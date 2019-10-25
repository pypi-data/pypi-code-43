from swimlane_platform.environment_updater.environment_updater_base import EnvironmentUpdaterBase
from swimlane_platform.lib import names, Configuration, info_function_start_finish, \
    VersionValidator, ContainingDirectoryExistsValidator


class EnvironmentUpdaterValidate(EnvironmentUpdaterBase):

    @info_function_start_finish('Swimlane validate.')
    def run(self):
        # type: () -> None
        """
        Main method.
        """
        self.docker_helper.containers_exists_validate(names.SW_API, names.SW_MONGO)
        local, remote = self.parse_file_location(self.config.args.report_file)
        command = ['validate', '-f', remote]
        # Not pulled up to parent, because in the future EU needs to be fixed.
        self.get_admin_connection()
        self.run_image_command(command, {local: {'bind': self.REPORT_FOLDER, 'mode': 'rw'}})


def run(config):
    # type: (Configuration) -> None
    questions = [
        {
            'type': 'input',
            'name': 'report_file',
            'message': 'Specify the path to the output validation report file.',
            'validate': ContainingDirectoryExistsValidator
        },
        {
            'type': 'input',
            'name': 'version',
            'message': 'Specify the version to validate.',
            'validate': VersionValidator
        }
    ]
    config.collect(questions)
    EnvironmentUpdaterValidate(config).run()
