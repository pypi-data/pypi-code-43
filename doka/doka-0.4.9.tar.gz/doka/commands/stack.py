from doka.kernel.repository.repositories import ProjectRepository, StackRepository
from doka.kernel.actions import stack


class Stack(object):

    def __init__(self, build: bool = False, branch: str = None, pull: str = None, project=None, join_network=None):
        self._flags = {
            "build": build,
            "branch": branch,
            "pull": pull,
            "join_network": join_network
        }
        if project:
            self._project = ProjectRepository().get_one(project)
        else:
            self._project = ProjectRepository().get_active()

    def build(self, name):
        stack.build(self._stack_entity(name))

    def up(self, name):
        stack_entity = self._stack_entity(name)
        if not stack_entity:
            print("Stack {} not defined".format(name))
            return
        project_entity = ProjectRepository().get_one(stack_entity.project_name)
        if self._flags.get("branch"):
            print("Checkout stack to branch: ", self._flags.get("branch"))
            stack.checkout(stack_entity, branch=self._flags.get("branch"))
        if self._flags.get("pull"):
            print("Pull data from remote origin")
            self._flags.pop("build", None)
            stack.pull(stack_entity)
        if self._flags.get("build"):
            print("Build images")
            stack.build(stack_entity)
        if self._flags.get("join_network"):
            stack.join_network(stack_entity, self._flags.get("join_network"))
        # stack.build(self._stack_entity(name))
        stack.up(stack_entity, project_entity)

    def down(self, name):
        stack.down(self._stack_entity(name))

    def restart(self, name):
        self.down(name)
        self.up(name)

    def _stack_entity(self, stack_name):
        return StackRepository(self._project).get_one(stack_name)
