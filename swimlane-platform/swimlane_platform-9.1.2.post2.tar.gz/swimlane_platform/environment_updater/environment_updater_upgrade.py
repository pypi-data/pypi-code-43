from swimlane_platform.environment_updater.environment_updater_base import EnvironmentUpdaterBase
from swimlane_platform.lib import info_function_start_finish, Configuration, names, ValidationException


class EnvironmentUpdaterUpgrade(EnvironmentUpdaterBase):

    @info_function_start_finish('Environment updater upgrade.')
    def run(self):
        # type: () -> None
        """
        Main method.
        """
        helper = self.docker_helper
        helper.containers_exists_validate(names.SW_WEB, names.SW_API, names.SW_TASKS, names.SW_MONGO)
        mongo_container = helper.container_get(names.SW_MONGO)
        if not mongo_container or mongo_container.status != 'running':
            raise ValidationException('Mongo container is not running upgrade is not possible.')
        helper.containers_run(helper.container_stop, names.SW_WEB, names.SW_API, names.SW_TASKS)
        command = ['upgrade']
        self.get_admin_connection()
        self.run_image_command(command, {})


def run(config):
    # type: (Configuration) -> None
    EnvironmentUpdaterUpgrade(config).run()
