import giga
from giga.configs import utils

log = giga.logs.get_logger(__name__)

class Debian(giga.Configuration):
  'Install Docker on a Debian system.'

  config_name        = 'docker.Debian'
  config_logger      = log
  config_os_packages = ['docker.io']

class CentOs7(giga.Configuration):
  'Install Docker on a CentOs7 system.'

  pass # FIXME

class DockerCompose(utils.CurlBins):
  'Install docker-compose on a system.'

  config_name     = 'docker.DockerCompose'
  config_logger   = log
  compose_version = '1.24.1'
  bin_dir         = '/usr/local/bin'

  def get_curl_bins(self):
    compose_url = 'https://github.com/docker/compose/releases/download/%s/docker-compose-Linux-x86_64' % self.compose_version
    return [(f'{self.bin_dir}/docker-compose', compose_url, f'{compose_url}.sha256', 'sha256')]
