'Run a shell command.'

import giga
from lura.attrs import ottr
from lura.formats import yaml
from lura.strutils import as_bool
from lura.time import poll
from shlex import quote

log = giga.logs.get_logger(__name__)

class Shell(giga.Configuration):

  config_name   = 'Shell'
  config_logger = log
  logger        = log
  log_level     = log.INFO
  shell         = '/bin/bash'

  def get_argv(self):
    return self.args[0]

  def on_apply_finish(self):
    with self.task('Run shell command', log) as task:
      argv = self.get_argv()
      res = self.system.run(f'{self.shell} -i -c {quote(argv)}')
      +task
    quiet = as_bool(self.kwargs.get('quiet', '0'))
    if not quiet:
      fmt = ottr(
        argv = res.command,
        code = res.return_code,
        stdout = res.stdout,
        stderr = res.stderr,
      )
      self.log('\n' + yaml.dumps(fmt).rstrip() + '\n')
    super().on_apply_finish()

  def on_is_applied(self):
    return False

class CurlBins(giga.Configuration):

  config_name   = 'utils.CurlBin'
  config_logger = log
  curl_bins     = None

  def get_curl_bins(self):
    return self.curl_bins or []

  def apply_curl_bins(self):
    sys = self.system
    curl_bins = self.get_curl_bins()
    for bin, url, sum_url, alg in self.get_curl_bins():
      with self.task(f'Apply {bin}', log) as task:
        if not sys.isfile(bin):
          sum = None
          if sum_url:
            sum = sys.wloads(sum_url).rstrip().split()[0]
          sys.wget(url, bin, sum, alg)
          +task
        if not sys.ismode(bin, 0o755):
          sys.chmod(bin, 0o755)
          +task

  def on_apply_fininsh(self):
    self.apply_curl_bins()
    super().on_apply_finish()

  def delete_curl_bins(self):
    curl_bins = self.get_curl_bins()
    for bin, _, _, _ in curl_bins:
      with self.task(f'Delete {bin}', log) as task:
        sys = self.system
        if not sys.isfile(bin):
          return
        sys.rmf(bin)
        +task

  def on_delete_start(self):
    super().on_delete_start()
    self.delete_curl_bins()

  def on_is_applied(self):
    sys = self.system
    bins = tuple(bin for (bin, _, _, _) in self.get_curl_bins())
    return (
      super().on_is_applied() and
      all(sys.isfile(bin) and sys.ismode(bin, 0o755) for bin in bins)
    )
