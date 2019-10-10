from doka.kernel.services import docker
from doka.kernel.definition.entities import StackEntity, ProjectEntity, UnitEntity
from doka.kernel.repository.repositories import UnitRepository
from doka.kernel.actions import unit
from doka.kernel.storage.yaml import YamlStorage
from doka.kernel.storage import hooks


def join_network(stack_entity: StackEntity, network_name: str):
    docker.Network().join(stack_entity, network_name)


def register_unit_in_compose_file(stack_entity: StackEntity, unit_entity: UnitEntity):
    storage = YamlStorage(stack_entity.compose_directory.joinpath(stack_entity.compose_file))
    storage.set(
        index='services',
        value={
            unit_entity.container_name: {
                'image': unit_entity.name,
                'env_file': '.{}.env'.format(unit_entity.name),
                'networks': ["_".join([stack_entity.project_name, stack_entity.network])]
            }
        }
    )
    storage.write()


def unregister_unit_in_compose_file(stack_entity: StackEntity, unit_entity: UnitEntity):
    storage = YamlStorage(stack_entity.compose_directory.joinpath(stack_entity.compose_file))
    storage.remove(
        index='services.{}'.format(unit_entity.container_name)
    )
    storage.write()


def deploy(project_entity: ProjectEntity, stack_entity: StackEntity):
    storage = YamlStorage(stack_entity.compose_directory.joinpath(stack_entity.compose_file))
    for unit_entity in UnitRepository(stack_entity.project_name).get_for_build(stack_entity.name):
        storage.set(
            index='services.{}.image'.format(unit_entity.container_name),
            value="{}/{}".format(project_entity.docker_registry, unit_entity.repo.split(":").pop().replace('.git', ''))
        )
        hooks.move_unit_environment_to_deploy(project_entity, unit_entity)
    storage.write(project_entity.metadir.joinpath('deploy', stack_entity.name).with_suffix('.yml'))


def build(stack_entity: StackEntity):
    for unit_entity in UnitRepository(stack_entity.project_name).get_for_build(stack_entity.name):
        try:
            unit.build(unit_entity)
        except Exception as e:
            print("!!!Cannot build unit {}. Error: ".format(unit_entity.name), str(e))


def up(stack_entity: StackEntity, project_entity: ProjectEntity):
    storage = YamlStorage(stack_entity.compose_directory.joinpath(stack_entity.compose_file))
    if not storage.read().get("services"):
        return
    environment = docker.Environment()
    environment.set_for_project(project_entity)
    environment.set_for_stack(stack_entity)
    docker.Network().create(stack_entity)
    docker.Volume().create(stack_entity)
    docker.Stack(stack_entity).up()


def down(stack_entity: StackEntity):
    storage = YamlStorage(stack_entity.compose_directory.joinpath(stack_entity.compose_file))
    if not storage.read().get("services"):
        return
    docker.Stack(stack_entity).down()


def checkout(stack_entity: StackEntity, branch: str):
    for unit_entity in UnitRepository(stack_entity.project_name).get_for_build(stack_entity.name):
        try:
            unit.checkout(unit_entity, branch, is_build=False)
        except Exception:
            print("!!!Cannot checkout repository: ", unit_entity.name)


def pull(stack_entity: StackEntity):
    for unit_entity in UnitRepository(stack_entity.project_name).get_for_build(stack_entity.name):
        try:
            unit.pull(unit_entity, is_build=True)
        except Exception:
            print("!!!Cannot pull unit: ", unit_entity.name)
