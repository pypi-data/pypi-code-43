from doka.kernel.repository.repositories import UnitRepository, ProjectRepository, StackRepository
from doka.kernel.definition.entities import UnitSchema, ProjectSchema, StackSchema
from doka.kernel.services.git import Git
import json


class Inspect(object):
    def __init__(self, project=None, filter=None, stack=None, name=None, full: bool = None):
        self._flags = {
            "project": project,
            "stack": stack,
            "name": name,
            "full": full
        }
        try:
            self._flags["filter"] = json.loads(filter)
        except:
            self._flags["filter"] = {}

        if project:
            self._project = ProjectRepository().get_one(project)
        else:
            self._project = ProjectRepository().get_active()

    def projects(self):
        projects = ProjectRepository().get()
        return self._represent(projects, ProjectSchema, ["name", "env", "active"])

    def stacks(self):
        stacks = StackRepository(project=self._project).get()
        return self._represent(stacks, StackSchema, ["name", "network"])

    def units(self):
        search_filter = self._flags.get("filter")
        if self._flags.get("stack"):
            search_filter["stack_name"] = self._flags.get("stack")
        if self._flags.get("project"):
            search_filter["project_name"] = self._flags.get("project")
        if self._flags.get("name"):
            search_filter["name"] = self._flags.get("stack")

        units = UnitRepository(self._project).get(search_filter or None)
        for unit in units:
            if unit.repo:
                unit.branch = Git(unit).get_branch()

        return self._represent(units, UnitSchema, ["name", "branch", "stack_name"])

    def _represent(self, collection, schema, brief: list):
        result = []
        for entity in schema(many=True).dump(collection).data:
            item = {}
            for k, v in entity.items():
                if v is None:
                    continue
                if not self._flags.get("full") and k not in brief:
                    continue
                item[k] = v
            result.append(item)
        return result
