from doka.kernel.repository.repositories import ProjectRepository, UnitRepository, StackRepository
from doka.kernel.definition.entities import ProjectSchema, UnitEntity, ProjectEntity
from doka.kernel.services.git import Git
from doka.config import doka_config
from doka.kernel.storage import hooks
from doka.kernel.actions import stack


class Project(object):
    def __init__(self):
        self._projects_repository = ProjectRepository()

    def init(self, name, project_repo, deploy_repo, workdir):
        try:
            project_entity = ProjectSchema().load({
                "name": name,
                "project_repo": project_repo,
                "deploy_repo": deploy_repo,
                "workdir": workdir,
                "metadir": str(doka_config.STORAGE_DIR.joinpath(*["projects", name])),
                "env": "dev"
            }).data
            self._clone_project(project_entity)
            ProjectRepository().save(project_entity)
            return 'Project registered'
        except Exception as e:
            return str(e)

    def remove(self, name):
        try:
            self._projects_repository.remove(name)
            return 'Project removed'
        except Exception as e:
            return str(e)

    def down(self):
        project_entity = self._projects_repository.get_active()
        for stack_entity in StackRepository(project_entity).get():
            stack.down(stack_entity)

    def up(self):
        project_entity = self._projects_repository.get_active()
        for stack_entity in StackRepository(project_entity).get():
            stack.up(stack_entity, project_entity)

    def pull(self):
        project_entity = self._projects_repository.get_active()

        self._clone_project(project_entity)

        hooks.project_post_sync(project_entity.name)
        hooks.move_project_environment_to_stack(project_entity)
        hooks.create_unstacked_stack(project_entity)

        for unit_entity in UnitRepository(project_entity).get_for_build():
            if not unit_entity.codedir.exists():
                Git(unit_entity).clone()
            hooks.move_unit_environment_to_stack(unit_entity)

    def deploy(self, release_branch):
        project_entity = self._projects_repository.get_active()
        unit_entity = UnitEntity(
            name="{}_deploy".format(project_entity.name),
            project_name=None,
            codedir=project_entity.metadir.joinpath("deploy"),
            repo=project_entity.deploy_repo,
            stack_name=None,
            image_name=None
        )
        git = Git(unit_entity)
        if not unit_entity.codedir.exists():
            git.clone()
        else:
            git.fetch(force=False)

        git.create_branch(release_branch)
        git.checkout(release_branch)

        for entry in unit_entity.codedir.iterdir():
            if entry.is_file():
                entry.unlink()
        for stack_entity in StackRepository(project_entity).get():
            if stack_entity.name not in ["dwh", "unstacked"]:
                stack.deploy(project_entity, stack_entity)
        try:
            git.commit('Release: {}'.format(release_branch))
            git.push()
        except Exception as e:
            pass

        git.merge('master')
        git.push()

    def _clone_project(self, project_entity):
        Git(UnitEntity(
            name=project_entity.name,
            project_name=None,
            codedir=project_entity.metadir,
            repo=project_entity.project_repo,
            stack_name=None,
            image_name=None
        )).clone()
