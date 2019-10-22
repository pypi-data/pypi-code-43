import giga

log = giga.logs.get_logger(__name__)

class RcLocal755(giga.Configuration):

  config_name     = 'centos7.RcLocal755'
  config_logger   = log
  unset_on_delete = False

  def apply_rc_local(self):
    sys = self.system
    with sys.task('Apply rc.local executable bit') as task:
      task.ensure.fs.mode('/etc/rc.d/rc.local', 0o755)

  def delete_rc_local(self):
    sys = self.system
    with sys.task('Delete rc.local executable bit') as task:
      if self.unset_on_delete:
        task.ensure.fs.mode('/etc/rc.d/rc.local', 0o644)

class Epel(giga.Configuration):

  config_name     = 'centos7.Epel'
  config_logger   = log
  os_package_urls = (
    ('epel-release', 'https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm'),
  )

class Ius(giga.Configuration):

  config_name     = 'centos7.Ius'
  config_logger   = log
  os_package_urls = (
    ('ius-release',  'https://centos7.iuscommunity.org/ius-release.rpm'),
  )
