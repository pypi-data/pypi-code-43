from doka.kernel.storage.json import ProjectStorage, UnitStorage, StackStorage
from doka.kernel.definition.entities import ProjectSchema, UnitSchema, StackSchema
from doka.kernel.repository.filters import entity_filter
from doka.kernel.repository.exceptions import *


class Repository:
    _collection = None
    _storage = None
    _schema = None
    _primary_field = None

    def get_one(self, value):
        for entity in self._collection:
            if getattr(entity, self._primary_field) == value:
                return entity
        return None

    def count(self):
        return len(self._collection)

    def get(self, search_filter: dict = None):
        if search_filter is None:
            return self._collection
        return list(filter(entity_filter(search_filter), self._collection))

    def remove(self, entity):
        for i, item in enumerate(self._collection):
            if getattr(item, self._primary_field) == getattr(entity, self._primary_field):
                del self._collection[i]
        self._flush()

    def save(self, entity):
        self._collection = [
            _e for _e in self._collection if
            getattr(_e, self._primary_field) != getattr(entity, self._primary_field)
        ]
        self._collection.append(entity)
        self._flush()

    def _flush(self):
        data = self._schema(many=True).dump(self._collection)
        self._storage.write(data.data)

    def _get_collection(self):
        data = self._storage.read()
        if data:
            return self._schema(many=True).load(data).data
        return []


class UnitRepository(Repository):
    def __init__(self, project):
        if isinstance(project, str):
            project = ProjectRepository().get_one(project)
        self._storage = UnitStorage(project)
        self._schema = UnitSchema
        self._primary_field = "name"
        self._collection = self._get_collection()

    def get_by_any_name(self, name):
        for unit in self._collection:
            if unit.name == name or unit.container_name == name:
                return unit

    def get_for_build(self, stack_name=None):
        result = []
        for unit in self._collection:
            if unit.repo is None:
                continue
            if stack_name and unit.stack_name != stack_name:
                continue
            result.append(unit)
        return result


class ProjectRepository(Repository):
    def __init__(self):
        self._storage = ProjectStorage()
        self._schema = ProjectSchema
        self._primary_field = "name"
        self._collection = self._get_collection()

    def get_active(self):
        for project in self._collection:
            if project.active:
                return project
        return None

    def set_active(self, project_name):
        for project in self._collection:
            project.active = project.name == project_name
        self._flush()


class StackRepository(Repository):
    def __init__(self, project):
        if isinstance(project, str):
            project = ProjectRepository().get_one(project)
        self._storage = StackStorage(project)
        self._schema = StackSchema
        self._primary_field = "name"
        self._collection = self._get_collection()
