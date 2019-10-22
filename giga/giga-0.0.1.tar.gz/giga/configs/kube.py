import giga
from giga.configs import utils

log = giga.logs.get_logger(__name__)

class Kubectl(utils.CurlBins):

  config_name     = 'kube.Kubectl'
  config_logger   = log
  kubectl_version = '1.15.4'
  bin_dir         = '/usr/local/bin'

  def get_curl_bins(self):
    kubectl_url = 'https://storage.googleapis.com/kubernetes-release/release/v%s/bin/linux/amd64/kubectl' % self.kubectl_version
    return [(f'{self.bin_dir}/kubectl', kubectl_url, f'{kubectl_url}.sha256', 'sha256')]

class Kc(giga.Configuration):

  config_name   = 'kube.Kc'
  config_logger = log
  bin_dir       = '/usr/local/bin'

  _kc = '#!/bin/sh\nexec kubectl "$@"\n'

  def apply_kc_bin(self):
    kc_path = f'{self.bin_dir}/kc'
    with self.task(f'Apply {kc_path}', log) as task:
      task.ensure.fs.contents(kc_path, self._kc)
      task.ensure.fs.mode(kc_path, 0o755)

  def delete_kc_bin(self):
    kc_path = f'{self.bin_dir}/kc'
    with self.task(f'Delete {kc_path}', log) as task:
      task.ensure.fs.absent(kc_path)

class ResourceConfiguration(giga.Configuration):

  config_logger  = log
  create_timeout = 120
  ready_timeout  = 120
  delete_timeout = 120
  poll_interval  = 0.3

  def get(self, type, name=None, namespace=None):
    argv = [f'kubectl get {type}']
    if name:
      argv.append(name)
    if namespace == '*':
      argv.append('--all-namespaces')
    elif namespace:
      argv.append(f'--namespace={namespace}')
    argv.apend('--output=json')
    argv = ''.join(argv)
    res = sys(argv, enforce=False)
    if res.return_code != 0:
      return None
    return json.loads(res.stdout)

  def is_deploy_created(self, deploy, namespace):
    deploys = self.get('deploy', namespace=namespace).items
    return any(deploy.metadata.name == deploy for deploy in deploys)

  def wait_for_deploy_create(self, deploy, namespace):
    with self.task(f'Wait for {deploy} create', log) as task:
      test = lambda: self.is_deploy_created(deploy, namespace)
      return poll(test, timeout=self.create_timeout, pause=self._poll_interval)

  def wait_for_pods_ready(self, getter):
    with self.task(f'Wait for pods ready', log) as task:
      def test():
        return all(
          all(status.ready for status in pod.containerStatuses)
          for pod in getter()
        )
      return poll(test, timeout=self.create_timeout, pause=self._poll_interval)
