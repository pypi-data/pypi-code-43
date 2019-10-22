'Netdata configurations.'

import giga
import io
from configparser import ConfigParser
from giga.configs import debian
from giga.configs import centos7
from lura.attrs import ottr
from lura.hash import hashs
from shlex import quote

log = giga.logs.get_logger(__name__)

class OsBase(giga.Configuration):
  '''
  Base class for all operating systems.

  - configure the python package manager api to use python2 rather than
    python3, because that's how netdata has chosen to live its life
  - install python packages common to all platforms
  '''

  config_logger          = log
  config_python_version  = 2
  config_python_packages = [
    'dnspython',
  ]
  config_keep_python_packages = False

class Debian(OsBase):
  '''
  Apply Debian packages needed by netdata and enable rc-local if using ksm.
  '''

  config_name    = 'netdata.Debian'
  config_include = [debian.RcLocal755]
  config_os_packages = [
    'zlib1g-dev',
    'uuid-dev',
    'libuv1-dev',
    'liblz4-dev',
    'libjudy-dev',
    'libssl-dev',
    'libmnl-dev',
    'gcc',
    'make',
    'git',
    'autoconf',
    'autoconf-archive',
    'autogen',
    'automake',
    'pkg-config',
    'curl',
    'python',
    'python-pip',
    'python-ipaddress',
    'lm-sensors',
    'libmnl0',
    'netcat',
  ]

class CentOs7(OsBase):
  '''
  Apply CentOs7 packages needed by netdata and enable rc-local if using ksm.
  '''

  config_name    = 'netdata.CentOs7'
  config_include = [
    centos7.Epel,
    centos7.Ius,
    centos7.RcLocal755
  ]
  config_os_packages = [
    'automake',
    'curl',
    'gcc',
    'git2u-core',
    'libmnl-devel',
    'libuuid-devel',
    'openssl-devel',
    'libuv-devel',
    'lz4-devel',
    'Judy-devel',
    'make',
    'pkgconfig',
    'python',
    'python-pip',
    'python-ipaddress',
    'zlib-devel',
    'lm_sensors',
    'libmnl',
    'nc',
  ]

class Package(giga.Configuration):
  '''
  Apply the netdata package and optionally arrange for ksm to be enabled
  at boot.

  ksm[1] is 'kernel samepage merging', a feature of the Linux kernel which can
  merge identical memory pages into a single copy-on-write page, thus
  introducing significant memory savings for certain workloads. The netdata
  authors claim that ksm can reduce netdata's memory usage by up to 60%.
  There's really no reason to disable it, but this is a base class, so we leave
  it to you.

  [1] https://en.wikipedia.org/wiki/Kernel_same-page_merging
  '''

  config_name   = 'netdata.Package'
  config_logger = log
  version       = '1.18.1'
  root_dir      = '/opt'
  apply_ksm     = True
  delete_ksm    = True
  ksm_interval  = 1000
  telemetry     = True

  _ksm = (
    'echo 1 >/sys/kernel/mm/ksm/run',
    'echo 1000 >/sys/kernel/mm/ksm/sleep_millisecs',
  )
  _ksm = '\n' + '\n'.join(_ksm) + '\n'

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

  def apply_ksm(self):
    with self.task('Apply kernel samepage merging') as task:
      if self.apply_ksm:
        task.ensure.fs.in_file('/etc/rc.local', self._ksm)
        task.ensure.fs.pseudofs('/sys/kernel/mm/ksm/run', 1)
        task.ensure.fs.pseudofs('/sys/kernel/mm/ksm/sleep_millisecs', 1000)

  def apply_netdata(self):
    with self.task('Apply netdata package') as task:
      sys = self.system
      if sys.exists(f'{self.root_dir}/netdata/etc/netdata'):
        return
      with sys.tempdir(prefix='netdata.') as temp_dir:
        repo_dir = f'{temp_dir}/netdata'
        repo_url = 'https://github.com/netdata/netdata'
        args = f'--dont-wait --dont-start-it --install {quote(self.root_dir)}'
        if not self.telemetry:
          args = f'{args} --disable-telemetry'
        sys(f'git clone {repo_url} {repo_dir}')
        sys(f'git checkout v{self.version}', cwd=repo_dir)
        sys(f'$SHELL netdata-installer.sh {args}', cwd=repo_dir)
      +task

  def on_apply_finish(self):
    self.apply_ksm()
    self.apply_netdata()
    super().on_apply_finish()

  def delete_netdata(self):
    with self.task('Delete netdata package') as task:
      sys = self.system
      dir = f'{self.root_dir}/netdata'
      if sys.exists(dir) and len(sys.ls(dir)) > 0:
        sys(f'{dir}/usr/libexec/netdata/netdata-uninstaller.sh -y -f')
        +task

  def delete_leftovers(self):
    with self.task('Delete leftover files') as task:
      path = '/etc/systemd/system/multi-user.target.wants/netdata.service'
      task.ensure.fs.absent(path)

  def delete_ksm(self):
    with self.task('Delete kernel samepage merging') as task:
      if self.delete_ksm:
        task.ensure.fs.not_in_file('/etc/rc.local', self._ksm)
        task.ensure.fs.pseudofs('/sys/kernel/mm/ksm/run', 0)

  def on_delete_start(self):
    super().on_delete_start()
    self.delete_netdata()
    self.delete_leftovers()
    self.delete_ksm()

  def on_is_applied(self):
    return (
      super().on_is_applied() and
      self.system.zero('systemctl is-enabled netdata')
    )

class Conf(giga.Configuration):
  '''
  Apply custom values to netdata.conf. This can be done in three ways:

  - set the class variable `conf_changes`
  - pass `conf_changes` to the constructor
  - override `get_conf_changes()` in a subclass

  `conf_changes` must be a list, and each item must be a list or
  tuple of:

    ('config section', 'variable name', 'new value')

  For example, to set the history limit to 24 hours:

    ('global', 'history', 86400)
  '''

  config_name   = 'netdata.Conf'
  config_logger = log
  root_dir      = '/opt'
  conf_changes  = None

  def get_conf_changes(self):
    return self.conf_changes or []

  def apply_conf_changes(self):
    conf_changes = self.get_conf_changes()
    if not conf_changes:
      return
    sys = self.system
    path = f'{self.root_dir}/netdata/etc/netdata/netdata.conf'
    config = ConfigParser()
    with io.StringIO(sys.loads(path)) as buf:
      config.read_file(buf)
    for section, key, value in conf_changes:
      with self.task(f'Apply netdata.conf {section}.{key}') as task:
        if value is None:
          raise ValueError(f'netdata.conf: {section}.{key}: value is None')
        value = str(value)
        if (
          section in config and
          key in config[section] and
          config[section][key] == value
        ):
          continue
        config.setdefault(section, {})
        config[section][key] = value
        +task
    with io.StringIO() as buf:
      config.write(buf)
      task.ensure.fs.contents(path, buf.getvalue())

  def on_apply_finish(self):
    self.apply_conf_changes()
    super().on_apply_finish()

class Healthd(giga.Configuration):
  '''
  Apply custom values to health.d conf files. This can be done in three ways:

  - set the class variable `healthd_changes`
  - pass `healthd_changes` to the constructor
  - override `get_healthd_changes()` in a subclass

  `healthd_changes` must be a list, and each item must be a list or tuple of:

    ('conf filename', {selector fields}, {update fields})

  For example, to silence the `ram_in_use` alarm on Linux:

   ('ram.conf', {'alarm': 'ram_in_use', 'os': 'linux'}, {'to': 'silent'})
  '''

  # FIXME allow the selector to be a callable to which we will pass a check;
  #       the callable would return True if the check matches, else False.
  #       the issue is that we need to provide a way to select on field
  #       presence, rather than field value. a user may know the field name
  #       but they may not reliably know its value to use in a selector

  config_name     = 'netdata.Healthd'
  config_logger   = log
  root_dir        = '/opt'
  healthd_changes = None

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

  def get_healthd_changes(self):
    return self.healthd_changes or []

  def load_checks(self, path):
    sys = self.system
    checks = []
    check = None
    with io.StringIO(sys.loads(path)) as buf:
      for line in buf:
        line = line.strip()
        if not line or line[0] == '#':
          continue
        k, v = line.split(': ', 1)
        if k in ('alarm', 'template'):
          check = ottr()
          checks.append(check)
        check[k] = v
    return checks

  def format_checks(self, checks):
    with io.StringIO() as buf:
      for check in checks:
        field_len = max(len(k) for k in check)
        for (k, v) in check.items():
          if v is None:
            # FIXME setting a field's value to None will remove the field
            #       entirely from the check. this is undesriable because then
            #       the field can no longer be matched by a selector. we should
            #       see if netdata can gracefully handle empty fields so that
            #       they don't need to be removed to be disabled
            continue
          k = '%s%s' % (' ' * (field_len - len(k)), k)
          buf.write(f'{k}: {v}\n')
        buf.write('\n')
      return buf.getvalue()

  def dump_checks(self, task, path, checks):
    sys = self.system
    contents = self.format_checks(checks)
    created = sys.backuponce(path)
    sys.dumps(path, contents)
    task + (1 + int(created))

  def apply_healthd_change(self, file, selector, update):
    with self.task(f'Apply health.d {file}') as task:
      path = f'{self.root_dir}/netdata/usr/lib/netdata/conf.d/health.d/{file}'
      checks = self.load_checks(path)
      sum_old = hashs(self.format_checks(checks))
      selected = tuple(
        check for check in checks
        if all(k in check and check[k] == v for (k, v) in selector.items())
      )
      if len(selected) == 0:
        return # FIXME what to do here
      for check in selected:
        for k in update:
          check[k] = update[k]
      sum_new = hashs(self.format_checks(checks))
      if sum_old != sum_new:
        self.dump_checks(task, path, checks)

  def apply_healthd_changes(self):
    healthd_changes = self.get_healthd_changes()
    for file, selector, update in healthd_changes:
      self.apply_healthd_change(file, selector, update)

  def on_apply_finish(self):
    self.apply_healthd_changes()
    super().on_apply_finish()

class CustomSender(giga.Configuration):
  '''
  Apply a custom_sender() bash function to health_alarm_notify.conf. This
  can be done in three ways:

  - set the class variable `custom_sender`
  - pass `custom_sender` to the constructor
  - override `get_custom_sender()` in a subclass
  '''

  config_name   = 'netdata.Notifications'
  config_logger = log
  root_dir      = '/opt'
  custom_sender = None

  def get_custom_sender(self):
    return self.custom_sender

  def apply_custom_sender(self):
    with self.task('Apply custom sender') as task:
      sys = self.system
      custom_sender = self.get_custom_sender()
      if not custom_sender:
        return
      dir = f'{self.root_dir}/netdata/usr/lib/netdata/conf.d'
      path = f'{dir}/health_alarm_notify.conf'
      with io.StringIO(sys.loads(path)) as cf, StringIO() as buf:
        while True:
          line = cf.readline()
          if line == '':
            break
          if line.rstrip() == 'DEFAULT_RECIPIENT_CUSTOM=""':
            buf.write('DEFAULT_RECIPIENT_CUSTOM="custom"\n')
            continue
          if line.rstrip() == 'custom_sender() {':
            buf.write(custom_sender)
            while True:
              line = cf.readline()
              if line == '':
                raise RuntimeError('Received EOF before end of custom_sender()')
              if line.rstrip() == '}':
                break
            continue
          buf.write(line)
        task.ensure.fs.contents(path, buf.getvalue())

  def on_apply_finish(self):
    self.apply_custom_sender()
    super().on_apply_finish()

  def on_is_applied(self):
    custom_sender = self.get_custom_sender()
    if not custom_sender:
      return super().on_is_applied()
    sys = self.system
    dir = f'{self.root_dir}/netdata/usr/lib/netdata/conf.d'
    path = f'{dir}/health_alarm_notify.conf'
    return (
      super().on_is_applied() and
      sys.exists(path) and
      sys.contains(path, custom_sender)
    )

  # FIXME we can implement a delete() by copying the custom_sender from the
  #       backup file we created during apply()

class Service(giga.Configuration):
  'Starts the netdata service on apply and stops it on delete.'

  config_name   = 'netdata.Service'
  config_logger = log

  def on_apply_start(self):
    super().on_apply_start()
    with self.task('Apply netdata service start') as task:
      task.ensure.systemd.enabled_and_started('netdata')

  def on_delete_start(self):
    super().on_delete_start()
    with self.task('Apply netdata service stop') as task:
      task.ensure.systemd.disabled_and_stopped('netdata')

  def on_is_applied(self):
    sys = self.system
    return (
      super().on_is_applied() and
      sys.zero('systemctl status netdata')
    )
