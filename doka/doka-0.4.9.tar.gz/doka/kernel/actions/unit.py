from doka.kernel.definition.entities import UnitEntity
from doka.kernel.services.git import Git
import doka.kernel.services.docker as docker


def build(unit_entity: UnitEntity):
    docker.Unit(unit_entity).build()


def checkout(unit_entity: UnitEntity, branch, is_build=True):
    git = Git(unit_entity)
    if git.get_branch() != branch:
        git.fetch()
    git.checkout(branch)
    if is_build:
        build(unit_entity)


def pull(unit_entity: UnitEntity, is_build=True):
    Git(unit_entity).pull()
    if is_build:
        build(unit_entity)


def fetch(unit_entity: UnitEntity):
    Git(unit_entity).fetch()


def start(unit_entity: UnitEntity):
    docker.Unit(unit_entity).start()


def stop(unit_entity: UnitEntity):
    docker.Unit(unit_entity).stop()


def restart(unit_entity: UnitEntity):
    docker.Unit(unit_entity).restart()


def scale(unit_entity: UnitEntity, num):
    docker.Unit(unit_entity).scale(num)


def mount(unit_entity: UnitEntity, folder=None):
    docker.Unit(unit_entity).mount(folder)
