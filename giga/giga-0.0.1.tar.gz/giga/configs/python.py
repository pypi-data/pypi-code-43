import giga

log = giga.logs.get_logger(__name__)

class EditablePackages(giga.Configuration):

  config_name       = 'python.EditablePackage'
  editable_packages = None
  synchronize       = False

  def get_editable_packages(self):
    return self.editable_packages or []

  def apply_editable_packages(self):
    sys = self.system
    for pkg, path in self.get_editable_packages():
      with self.task(f'Apply {pkg}') as task:
        if pkg in self.packages.pip:
          continue
        if self.synchronize:
          with task.synchronized():
            sys(f'{sys.python} -m pip install -e {path}')
        else:
          sys(f'{sys.python} -m pip install -e {path}')
        +task

  def on_apply_start(self):
    super().on_apply_start()
    self.apply_editable_packages()

  def delete_editable_packages(self):
    sys = self.system
    for pkg, path in self.get_editable_packages():
      with self.task(f'Delete {pkg}') as task:
        if pkg not in self.packages.pip:
          continue
        if self.synchronize:
          with task.synchronized():
            sys(f'{sys.python} setup.py develop -u', cwd=path)
        else:
          sys(f'{sys.python} setup.py develop -u', cwd=path)
        +task

  def on_delete_start(self):
    super().on_delete_start()
    self.delete_editable_packages()
