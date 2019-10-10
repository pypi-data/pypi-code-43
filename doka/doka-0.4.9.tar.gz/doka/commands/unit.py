from doka.kernel.definition.entities import UnitEntity
from doka.kernel.services.git import Git
from doka.kernel.repository.repositories import UnitRepository, ProjectRepository, StackRepository
from doka.kernel.storage import hooks
from doka.kernel.storage.code import CodeStorage
from doka.kernel.actions import unit, stack
from doka.kernel.services import docker, tester


class Unit(object):

    def __init__(self, template=None, repo=None, stack=None, project=None, branch=None, pull: bool = None,
                 dev: bool = None, ports: str = None, name: str = None, build: bool = None,
                 no_cache: bool = None, mount=None):
        self._flags = {
            "template": template,
            "repo": repo,
            "stack": stack,
            "branch": branch,
            "pull": pull,
            "dev": dev,
            "mount": mount,
            "ports": ports,
            "name": name,
            "build": build,
            "no_cache": no_cache
        }
        if project:
            self._project = ProjectRepository().get_one(project)
        else:
            self._project = ProjectRepository().get_active()

    def bootstrap(self, unit_name):
        template = self._flags.get("template")
        repo = self._flags.get("repo")
        stack = self._flags.get("stack")

        if not template:
            return 'Error: template not defined'
        if not stack:
            return 'Error: stack not defined'

        try:

            unit_entity = UnitEntity(
                name=unit_name,
                project_name=self._project.name,
                repo=template,
                codedir=self._project.workdir.joinpath(*[stack, unit_name]),
                stack_name=stack
            )
            git = Git(unit_entity)
            git.clone(from_template=True)
            git.init()
            if repo:
                unit_entity.repo = repo
                git = Git(unit_entity)
                git.add_origin(push_initial_commit=True)
            git.create_branch("development")

            unit_repository = UnitRepository(self._project)
            unit_repository.save(unit_entity)

        except Exception as e:
            return str(e)

    def build(self, unit_name):
        self._flags["build"] = None
        unit_entity = self._get_unit(unit_name)
        docker.Unit(unit_entity).build(self._flags.get("no_cache"))

    def get(self, repo):
        unit_name = self._flags.get("name")
        if not unit_name:
            unit_name = repo.split('/').pop().replace(".git", "")
        stack_entity = StackRepository(self._project).get_one(self._flags.get("stack") or 'unstacked')
        if not stack_entity:
            return 'Stack {} not defined'.format(stack_entity.name)
        unit_repository = UnitRepository(self._project)
        unit_entity = unit_repository.get_by_any_name(unit_name)

        if not unit_entity:
            unit_entity = UnitEntity(
                name=".".join([stack_entity.name, unit_name]),
                project_name=self._project.name,
                repo=repo,
                codedir=self._project.workdir.joinpath(*[stack_entity.name, unit_name]),
                stack_name=stack_entity.name,
                working_dir='/code'
            )
        git = Git(unit_entity)
        if not unit_entity.codedir.exists():
            git.clone()
            if self._flags.get('branch'):
                git.checkout(self._flags.get("branch"))
        else:
            if self._flags.get('branch'):
                git.checkout(self._flags.get("branch"))
            git.pull()
        try:
            unit_repository.save(unit_entity)
        except:
            pass
        stack.register_unit_in_compose_file(stack_entity, unit_entity)
        hooks.move_unit_environment_to_stack(unit_entity)
        if self._flags.get("build"):
            docker.Unit(unit_entity).build(self._flags.get("no_cache"))

    def test(self, unit_name):
        unit_entity = UnitRepository(self._project).get_by_any_name(unit_name)
        if not unit_entity:
            return 'Unit not found'
        tester.Unit(unit_entity).test_api()

    def up(self, unit_name):
        try:
            unit.start(self._get_unit(unit_name))
        except Exception as e:
            return str(e)

    def down(self, unit_name):
        try:
            unit.stop(self._get_unit(unit_name))
        except Exception as e:
            return str(e)

    def restart(self, unit_name):
        try:
            unit.restart(self._get_unit(unit_name))
        except Exception as e:
            return str(e)

    def scale(self, unit_name, num):
        try:
            unit_entity = UnitRepository(self._project).get_by_any_name(unit_name)
            unit.scale(unit_entity, num)
        except Exception as e:
            return str(e)

    def remove(self, unit_name):
        repository = UnitRepository(self._project)
        unit_entity = repository.get_by_any_name(unit_name)
        if not unit_entity:
            return "Unit not found"
        stack_entity = StackRepository(self._project).get_one(unit_entity.stack_name)
        try:
            unit.stop(unit_entity)
        except Exception as e:
            print("Unit is not running. Skip stopping...")
        repository.remove(unit_entity)
        CodeStorage(unit_entity.codedir).remove()
        stack.unregister_unit_in_compose_file(stack_entity, unit_entity)
        hooks.delete_unit_environment_from_stack(unit_entity)
        return "Unit {} has been removed".format(unit_name)

    def _get_unit(self, unit_name):
        unit_entity = UnitRepository(self._project).get_by_any_name(unit_name)
        if self._flags.get("mount"):
            unit.mount(unit_entity, self._flags.get("mount"))
        if self._flags.get("branch"):
            unit.checkout(unit_entity, self._flags.get("branch"), False)
        if self._flags.get("pull"):
            unit.pull(unit_entity)
        if self._flags.get("build"):
            docker.Unit(unit_entity).build(self._flags.get("no_cache"))
        hooks.move_unit_environment_to_stack(unit_entity)
        return unit_entity
