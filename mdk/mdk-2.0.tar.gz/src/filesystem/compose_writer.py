"""ComposeWriter class"""
# pylint: disable=too-many-instance-attributes
from copy import deepcopy

from . import f_utils
from .config import Config


class ComposeWriter():
    """Manage and modify the yaml configuration of a docker-compose service"""
    def __init__(self):
        self.auth_key = None
        self.base_image = None
        self.bind_mdkshared = None
        self.bind_mount = None
        self.default_shell = None
        self.directory = None
        self.gen_dockerfile = None
        self.set_host_uid = None
        self.keep_alive = None
        self.mount_source = None
        self.mount_target = None
        self.name = None
        self.set_ros_logs = None
        self.share_ssh_auth = None
        self.share_x11 = None
        self.sub_directory = None
        self.use_data_volume = None
        self.use_env = None


    @staticmethod
    def add_env_var(compose_service, idx, val):
        """add environment variable to a service object"""
        modified_service = deepcopy(compose_service)
        if "environment" in modified_service:
            modified_service["environment"][idx] = val
        else:
            modified_service["environment"] = {idx: val}
        return modified_service


    @staticmethod
    def add_volume(compose_service, volume):
        """add volume to a service object"""
        modified_service = deepcopy(compose_service)
        if "volumes" in modified_service:
            modified_service["volumes"].append(volume)
        else:
            modified_service["volumes"] = [volume]
        return modified_service


    def build_config(self):
        """build configuration object to be inserted into docker-compose.yaml"""
        compose_service = {}

        if self.gen_dockerfile:
            compose_service["build"] = f_utils.path_to_relative_str(self.directory)
        else:
            compose_service["image"] = self.base_image

        if self.use_env:
            f_utils.touch_local_env()
            compose_service["env_file"] = ".env"

        if self.bind_mount:
            compose_service = ComposeWriter.add_volume(
                compose_service,
                "./{}:{}".format(
                    f_utils.path_to_relative_str(self.mount_source),
                    str(self.mount_target)
                )
            )
            compose_service["working_dir"] = str(self.mount_target)

        if self.share_ssh_auth:
            compose_service = ComposeWriter.add_env_var(
                compose_service,
                "SSH_AUTH_SOCK",
                "$SSH_AUTH_SOCK",
            )
            compose_service = ComposeWriter.add_volume(
                compose_service,
                "$SSH_AUTH_SOCK:$SSH_AUTH_SOCK",
            )

        if self.share_x11:
            compose_service = ComposeWriter.add_env_var(
                compose_service,
                "DISPLAY",
                "$DISPLAY",
            )
            compose_service = ComposeWriter.add_env_var(
                compose_service,
                "NVIDIA_DRIVER_CAPABILITIES",
                "compute,utility,graphics",
            )
            compose_service = ComposeWriter.add_volume(
                compose_service,
                "/tmp/.X11-unix:/tmp/.X11-unix",
            )

        if self.set_ros_logs:
            compose_service = ComposeWriter.add_env_var(
                compose_service,
                "ROS_LOG_DIR",
                "/tmp/roslogs",
            )
            compose_service = ComposeWriter.add_env_var(
                compose_service,
                "ROS_HOME",
                "/tmp/roslogs",
            )

        if self.set_host_uid:
            compose_service = ComposeWriter.add_env_var(
                compose_service,
                "HOST_UID",
                "$UID",
            )

        if self.bind_mdkshared:
            compose_service = ComposeWriter.add_volume(
                compose_service,
                "~/mdkshared:/mdkshared",
            )

        if self.use_data_volume:
            compose_service = ComposeWriter.add_volume(
                compose_service,
                {
                    "type": "volume",
                    "read_only": True,
                    "source": "data",
                    "target": "/pub/datasets",
                    "volume": {
                        "nocopy": True,
                    },
                }
            )

        # if user wants to keep the container alive, always add a docker-compose command.
        # otherwise, the default command is to run the shell. If a Dockerfile is generated,
        # this (and entrypoint location) are specified in the Dockerfile. If no Dockerfile is
        # generated, we must specify both the default command and entrypoint location in the conf
        if self.keep_alive:
            compose_service["command"] = "top -b"
        elif not self.gen_dockerfile:
            compose_service["command"] = self.default_shell

        return compose_service


    @staticmethod
    def write_dev_config():
        """write a dev override file using a list of service names"""
        config = Config()

        if config.working_dir is None:
            return

        original_compose_contents = f_utils.read_compose_yaml(
            file_path=config.working_dir/"docker-compose.yaml",
        )
        if original_compose_contents is None or "services" not in original_compose_contents:
            return

        shared_mount = "{}:{}".format(
            config.host_shared_path,
            config.target_shared_path,
        )

        service_contents = {"volumes": [shared_mount]}
        service_blocks = {}

        for service, _ in original_compose_contents["services"].items():
            service_blocks[service] = deepcopy(service_contents)

        compose_contents = {
            "version": original_compose_contents["version"],
            "services": service_blocks,
        }

        f_utils.write_compose(config.working_dir, compose_contents, extension="dev")
        return


    def write_dockerfile(self):
        """Write a new dockerfile to the service's directory"""
        if not self.gen_dockerfile:
            return

        dockerfile_lines = ["FROM {}".format(self.base_image), ""]
        dockerfile_lines.append("CMD [\"{}\"]".format(self.default_shell))
        f_utils.new_file("Dockerfile", self.directory, dockerfile_lines)


    def write_service_to_config(self):
        """save service configuration to docker-compose.yaml"""
        compose_service = self.build_config()
        f_utils.service_to_local_compose(self.name, compose_service)
