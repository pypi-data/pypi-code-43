from doka.kernel.repository.repositories import ProjectRepository


class Config:
    def set_active_project(self, project_name):
        repository = ProjectRepository()
        project_entity = repository.get_one(project_name)
        if not project_entity:
            return "Project {} not found".format(project_name)
        repository.set_active(project_entity.name)
        return 'Project {} set as active'.format(project_name)
