import subprocess
from doka.kernel.definition.entities import UnitEntity, ProjectEntity, StackEntity
from doka.kernel.storage.yaml import YamlStorage
from doka.kernel.repository.repositories import UnitRepository, StackRepository
from doka.kernel.storage.hooks import move_unit_environment_to_stack, move_project_environment_to_stack


class Runtime:
    def get_unit_ip(self, unit_entity: UnitEntity):
        return subprocess.check_output(
            "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' " + "_".join([
                unit_entity.project_name,
                unit_entity.container_name,
                '1'
            ]),
            shell=True).decode().strip()


class Environment:
    def set_for_stack(self, stack: StackEntity):
        units_repository = UnitRepository(stack.project_name)
        for unit in units_repository.get({"stack_name": stack.name, "repo": {"$neq": None}}):
            self.set_for_unit(unit)

    def set_for_project(self, project: ProjectEntity):
        move_project_environment_to_stack(project)

    @staticmethod
    def set_for_unit(unit: UnitEntity):
        move_unit_environment_to_stack(unit)


class Volume:
    def create(self, stack: StackEntity):
        if not stack.volumes:
            return
        for name, settings in stack.volumes.items():
            if settings is not None and settings.get("external"):
                subprocess.run(
                    "docker volume create {name} || true".format(
                        name=name
                    ),
                    shell=True,
                    check=True
                )


class Network:
    def create(self, stack: StackEntity):
        subprocess.run(
            "docker network create {name} || true".format(
                name="_".join([stack.project_name, stack.network])
            ),
            shell=True,
            check=True
        )

    def join(self, stack: StackEntity, network_name: str):
        compose_file = stack.compose_directory.joinpath(stack.compose_file)
        storage = YamlStorage(compose_file)
        storage.append("networks", {network_name: {"external": True}})
        storage.append("services.*.networks", network_name)


class Unit:
    def __init__(self, unit: UnitEntity):
        self._unit = unit
        self._stack = StackRepository(self._unit.project_name).get_one(unit.stack_name)

    def mount(self, folder_str):
        compose_file = self._stack.compose_directory.joinpath(self._stack.compose_file)
        storage = YamlStorage(compose_file)
        storage.set(
            "services.{}.volumes".format(self._unit.name.split(".")[1]),
            ["{}:{}".format(str(self._unit.codedir.joinpath(folder_str)), self._unit.working_dir)]
        )
        storage.write()

    def build(self, no_cache=None):
        subprocess.run(
            "docker build -t {name} {no_cache} {directory}".format(
                name=self._unit.image_name,
                directory=self._unit.codedir,
                no_cache='--no-cache' if no_cache else ''
            ),
            shell=True,
            check=True
        )

    def start(self):
        subprocess.run(
            "cd {directory} && docker-compose -p {project_name} -f {compose_file} up -d {container_name}".format(
                project_name=self._unit.project_name,
                compose_file=self._stack.compose_file,
                directory=self._stack.compose_directory,
                container_name=self._unit.container_name
            ),
            shell=True,
            check=True
        )

    def stop(self):
        subprocess.run(
            "cd {directory} && docker-compose -p {project_name} -f {compose_file} stop {container_name} && "
            "docker-compose -p {project_name} -f {compose_file} rm -f {container_name}".format(
                project_name=self._unit.project_name,
                compose_file=self._stack.compose_file,
                directory=self._stack.compose_directory,
                container_name=self._unit.container_name
            ),
            shell=True,
            check=True
        )

    def restart(self):
        subprocess.run(
            "cd {directory} && docker-compose -p {project_name} -f {compose_file} restart {container_name}".format(
                project_name=self._unit.project_name,
                compose_file=self._stack.compose_file,
                directory=self._stack.compose_directory,
                container_name=self._unit.container_name
            ),
            shell=True,
            check=True
        )

    def scale(self, num):
        subprocess.run(
            "cd {directory} && docker-compose -p {project_name} -f {compose_file} scale {container_name}={num}".format(
                project_name=self._unit.project_name,
                compose_file=self._stack.compose_file,
                directory=self._stack.compose_directory,
                container_name=self._unit.container_name,
                num=num
            ),
            shell=True,
            check=True
        )


class Stack:
    def __init__(self, stack: StackEntity):
        self._stack = stack

    def up(self):
        subprocess.run(
            "cd {directory} && docker-compose -p {project_name} -f {compose_file} up -d".format(
                project_name=self._stack.project_name,
                compose_file=self._stack.compose_file,
                directory=self._stack.compose_directory
            ),
            shell=True,
            check=True
        )

    def down(self):
        subprocess.run(
            "cd {directory} && docker-compose -p {project_name} -f {compose_file} down".format(
                project_name=self._stack.project_name,
                compose_file=self._stack.compose_file,
                directory=self._stack.compose_directory
            ),
            shell=True,
            check=True
        )
