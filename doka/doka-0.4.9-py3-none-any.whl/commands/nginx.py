from doka.plugins.nginx import nginx
from doka.kernel.repository.repositories import ProjectRepository


class Nginx(object):

    def __init__(self, exclude=None):
        self._project = ProjectRepository().get_active()
        self._exclude = exclude.split(',') or []

    def up(self):
        nginx.start(self._project, self._exclude)

    def restart(self):
        nginx.start(self._project, self._exclude)

    def down(self):
        nginx.stop(self._project)

    def update_hosts(self):
        try:
            count = nginx.update_hosts(self._project)
            return "{} hosts has added".format(count) if count else "No new hosts"
        except PermissionError:
            return "Permission denied. Use sudo to run this command"
