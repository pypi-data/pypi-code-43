import giga

log = giga.logs.get_logger(__name__)

class RcLocal755(giga.Configuration):
  '''
  Create /etc/rc.local if it doesn't exist and make it executable.
  '''

  unset_on_delete = False

  def apply_rc_local(self):
    sys = self.system
    with self.task('Apply rc.local executable bit', log) as task:
      path = '/etc/rc.local'
      if not sys.exists(path):
        task.ensure.contents(path, '#!/bin/bash\n')
      task.ensure.mode(path, 0o755)

  def delete_rc_local(self):
    sys = self.system
    with self.task('Delete rc.local executable bit', log) as task:
      if self.unset_on_delete:
        task.ensure.fs.mode('/etc/rc.local', 0o644)
