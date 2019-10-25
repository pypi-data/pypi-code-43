from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec


def load_modules(cli):
    for path in Path(__file__).resolve().parent.joinpath('tasks').iterdir():
        file_name = str(path)
        if file_name.endswith(".py"):
            module_name = file_name[:-3]
            task_spec = spec_from_file_location(module_name, file_name)
            task_module = module_from_spec(task_spec)
            task_spec.loader.exec_module(task_module)
            if hasattr(task_module, 'load'):
                task_module.load(cli)
