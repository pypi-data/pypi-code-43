import giga
from giga.configs import kube
from lura.time import poll
from shlex import quote

log = giga.logs.get_logger(__name__)

class Helm(giga.Configuration):
  'Apply Helm binaries to a system.'

  config_name   = 'helm.Helm'
  config_logger = log
  helm_version  = '2.14.3'
  bin_dir       = '/usr/local/bin'

  _helm_bins = ['linux-amd64/helm', 'linux-amd64/tiller']

  @property
  def helm_url(self):
    return 'https://get.helm.sh/helm-v%s-linux-amd64.tar.gz' % self.helm_version

  def apply_helm_bin(self, tar, bin):
    path = f'{self.bin_dir}/{os.path.basename(bin)}'
    with self.task(f'Apply {path}', log) as task:
      sys = self.system
      if not sys.isfile(path):
        if not sys.exists(tar):
          sum = sys.wloads(f'{self.helm_url}.sha256').rstrip()
          sys.wget(self.helm_url, tar, sum, 'sha256')
        sys(f"tar xf {tar} -C {self.bin_dir} --strip=1 {bin}")
        +task
      task.ensure.fs.mode(path, 0o755)

  def apply_helm_bins(self):
    with self.system.tempdir() as temp_dir:
      tar = f'{temp_dir}/helm.tgz'
      for bin in self._helm_bins:
        self.apply_helm_bin(tar, bin)

  def on_apply_finish(self):
    self.apply_helm_bins()
    super().on_apply_finish()

  def delete_helm_bins(self):
    sys = self.system
    for bin in self._helm_bins:
      path = f'{self.bin_dir}/{bin}'
      with self.task(f'Delete {path}', log) as task:
        task.ensure.fs.absent(path)

  def on_delete_start(self):
    super().on_delete_start()

class Tiller(kube.ResourceConfiguration):
  'Apply Tiller to a cluster.'

  config_name    = 'helm.Tiller'
  config_logger  = log
  history_max    = 200
  create_timeout = 10
  ready_timeout  = 10
  force_delete   = False

  _poll_interval = 0.2

  def get_pods(self):
    return tuple(
      pod for pod in self.get('pod', namespace='kube-system').items
      if pod.metadata.name.startswith('tiller-deploy-')
    )

  def apply_helm_init(self):
    with self.task('Apply tiller', log) as task:
      sys = self.system
      if not self.tiller_started:
        sys(f'helm init --history-max {self.history_max}')
        +task

  def on_apply_finish(self):
    self.apply_helm_init()
    self.wait_for_deploy_create('tiller-deploy', 'kube-system')
    self.wait_for_pods_ready(self.get_pods)

  def apply_helm_reset(self):
    with self.task('Apply helm reset', log) as task:
      if self.tiller_started:
        if self.force_delete:
          sys('helm reset --force')
        else:
          sys('helm reset')
        +task

  def on_delete_start(self):
    super().on_delete_start()
    self.apply_helm_reset()
    # FIXME wait

class HelmChart(kube.ResourceConfiguration):

  config_name   = 'helm.HelmChart'
  config_logger = log
  helm_charts   = None
  purge_delete  = True

  def get_helm_charts(self):
    return self.helm_charts or []

  def apply_helm_charts(self):
    helm_charts = self.get_helm_charts()
    for chart, name, values in helm_charts:
      with self.task(f'Apply {name}', log) as task:
        sys = self.system
        if sys.zero(f'helm status {name}'):
          return
        argv = [f'helm install {chart} --name {name}']
        for opt, val in values:
          argv.append(f'--set {quote(opt)}={quote(str(val))}')
        argv = ' '.join(argv)
        sys(argv)
        +task

  def on_apply_start(self):
    super().on_apply_start()
    self.apply_helm_charts()

  def delete_helm_charts(self):
    helm_charts = self.get_helm_charts()
    for _, name, _ in helm_charts:
      with self.task(f'Delete {name}', log) as task:
        sys = self.system
        if sys.nonzero(f'helm status {name}'):
          return
        if self.purge_delete:
          sys(f'helm delete --purge {name}')
        else:
          sys(f'helm delete {name}')
        +task

  def on_delete_start(self):
    super().on_delete_start()
    self.delete_helm_charts()

class DockerRegistry(HelmChart):

  config_name   = 'helm.DockerRegistry'
  config_logger = log
  helm_charts   = (
    (
      'stable/docker-registry',
      'docker-registry',
      {
        'persistence.enabled': 'true',
        'service.type': 'NodePort',
        'service.nodePort': 3200,
      },
    ),
  )

  def get_pods(self):
    return tuple(
      pod for pod in self.get('pod', namespace='default').items
      if pod.metadata.name.startswith('docker-registry-')
    )

  def on_apply_finish(self):
    self.wait_for_deploy_create('docker-registry', namespace='default')
    self.wait_for_pods_ready(self.get_pods)
    super().on_apply_finish()
