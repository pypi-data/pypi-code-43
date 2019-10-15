import copy
import os
import runpy
import sys
from contextlib import contextmanager
from pathlib import Path
from pprint import pformat

from p10s.base import BaseContext
from p10s.values import values


@contextmanager
def _global_state(dir, extra_sys_paths):
    here = os.getcwd()
    sys_path = copy.copy(sys.path)
    try:
        os.chdir(str(dir))
        sys.path = [str(path) for path in extra_sys_paths] + sys.path
        yield
    finally:
        os.chdir(here)
        sys.path = sys_path


CONTEXTS = []


def register_context(context):
    CONTEXTS.append(context)


def _stderr(*args):
    print(*args, file=sys.stderr)


class P10SScript:
    def __init__(self, filename):
        self.filename = filename
        self.base_dir = filename.parent
        self.contexts = []
        self.pyterranetes_dir = self._find_pyterranetes_dir(filename.parent)

    def render(self, verbose=False):
        for c in self.contexts:
            with _global_state(
                dir=self.base_dir, extra_sys_paths=[self.pyterranetes_dir]
            ):
                if verbose:
                    _stderr(
                        "  Rendering", pformat(c), "to", c.output, "in", self.base_dir
                    )
                c.render()
        return self

    def compile(self, verbose=False):
        if verbose:
            _stderr("Compiling", self.filename)
        with values({"p10s": {"file": self.filename}}):
            with _global_state(
                dir=self.base_dir, extra_sys_paths=[self.pyterranetes_dir]
            ):
                CONTEXTS.clear()
                globals = runpy.run_path(str(self.filename))
                for value in globals.values():
                    if isinstance(value, BaseContext):
                        self.contexts.append(value)
                self.contexts.extend(CONTEXTS)
        return self

    def _find_pyterranetes_dir(self, root):
        here = root
        count = 0
        while True:
            maybe = here / "pyterranetes"
            if maybe.exists() and maybe.is_dir():
                return maybe
                break
            if str(here) == here.root:
                break
            here = here.parent

            if count > 1000:
                raise Exception("Directory tree too deep. aborting")
            count += 1


class Generator:
    def _p10s_scripts(self, root):
        if not root.exists():
            raise FileNotFoundError("%s does not exist." % str(root))
        if root.is_file():
            yield root
        else:
            for dirname, sub_dirs, files in os.walk(str(root)):
                for file in files:
                    path = Path(file)
                    if path.suffix == ".p10s":
                        yield Path(os.path.join(dirname, file))

    def generate(self, root, verbose=False):
        root = Path(root).resolve()
        scripts = [
            P10SScript(filename=filename) for filename in self._p10s_scripts(root)
        ]
        for script in scripts:
            try:
                script.compile(verbose=verbose).render(verbose=verbose)
            except Exception as e:
                if verbose:
                    _stderr("Error while generating %s", script.filename)
                raise e
