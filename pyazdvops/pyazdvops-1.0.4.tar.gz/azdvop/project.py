import logging
from redishttp import HttpClient

logger = logging.getLogger(__name__)

class Project():
  _client = HttpClient('')
  _organization = ''
  _project = {}

  def __init__(self, pat, organization, project, redis_host = 'localhost', redis_port = 6379, redis_password = None, cache_expiry = 1):
    self._client = HttpClient(pat)
    self._organization = organization
    self._project = self.load_project()
  
  def load_project(self):
    return self._client.get('https://dev.azure.com/petronasvsts/_apis/projects/{}'.format(self._project))

  