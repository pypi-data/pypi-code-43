import giga
import os
from giga.configs import utils
from lura import net
from lura.time import poll
from shlex import quote
from time import sleep

log = giga.logs.get_logger(__name__)

class Debian(giga.Configuration):
  'Apply Debian packages needed to run Minikube with vm driver `none`.'

  config_name        = 'minikube.Debian'
  config_logger      = log
  config_os_packages = [
    'docker.io',
    'socat',
  ]

class Minikube(utils.CurlBins):
  'Apply the minikube binary to a system.'

  config_name      = 'minikube.Minikube'
  config_logger    = log
  minikube_version = 'latest'
  minikube_url     = 'https://storage.googleapis.com/minikube/releases/%s/minikube-linux-amd64' % minikube_version
  curl_bins        = (
    ('/usr/local/bin/minikube', minikube_url, f'{minikube_url}.sha256', 'sha256')
  )

class Addons(giga.Configuration):

  config_name   = 'minikube.Addons'
  config_logger = log
  enable        = None
  disable       = None

  def get_addons(self):
    return self.enable or [], self.disable or []

  def get_addon_status(self):
    return dict(
      line[3:].rstrip().split(': ', 1)
      for line in sys.lines('minikube addons list')
    )

  def apply_addons(self):
    enable, disable = self.get_addons()
    status = self.get_addon_status()
    for addon in enable:
      with self.task(f'Apply addon enable {addon}', log) as task:
        if status[addon] == "disabled":
          sys(f'minikube addons enable {addon}')
          +task
    for addon in disable:
      with self.task(f'Apply addon disable {addon}', log) as task:
        if status[addon] == "enabled":
          sys(f'minikube addons disable {addon}')
          +task

  def on_apply_start(self):
    super().on_apply_start()
    self.apply_addons()

class Cluster(giga.Configuration):
  'Apply a minikube cluster to a system.'

  config_name    = 'minikube.Cluster'
  config_logger  = log
  kube_version   = '1.15.4'
  vm_driver      = 'none'

  def apply_cluster(self):
    with self.task('Apply minikube cluster', log) as task:
      sys = self.system
      if sys.zero('minikube status'):
        return
      sys("minikube start --kubernetes-version='v%s' --vm-driver=%s" % (
        self.kube_version, self.vm_driver))
      sys('kubectl cluster-info')
      sys('minikube addons enable ingress')
      sys('minikube addons enable storage-provisioner')
      +task

  def on_apply_finish(self):
    self.apply_cluster()
    super().on_apply_finish()

  def delete_cluster(self):
    with self.task(f'Delete cluster', log) as task:
      sys = self.system
      if sys.nonzero('minikube status'):
        return
      sys('minikube delete')
      +task

  def on_delete_start(self):
    super().on_delete_start()
    self.delete_cluster()

  def on_is_applied(self):
    return (
      super().on_is_applied() and
      sys.zero('minikube status')
    )
