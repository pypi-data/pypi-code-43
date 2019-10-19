#!/usr/bin/env python
try:
    import win32api
except:
    # not available on linux
    pass
from docopt import docopt
import shutil
import subprocess
import shlex
import os
from os.path import join
import sys
from setuptools import find_packages
import yaml
from .defaultlog import log

TEMPLATES = os.path.abspath(join(__file__, os.pardir, os.pardir, "templates"))
ignorefolders = ["nbs", "docs", "models", "data", "env", "venv"]
opts = None

def main():
    """
    Zero configuration to create and publish html documentation

    Usage:
        autogen (docs|rst|html)... [options]

    options:
      -h, --help       Display this help message
      --projects=list  list of sub-projects to document. default assumes single project.
      --docs=DIR       docs folder [default: docs]

    commands:
      docs   Initialise index.rst, conf.py and gitlab-ci for docs
      rst    Create rst docstrings in docs/_rst
      html   Create html docs in docs/_build/html

    To automatically create and publish docs every commit see ".gitlab-ci.yml"
    """
    global opts
    opts = docopt(main.__doc__)
    log.info(opts)

    # run from root
    root = get_project_root()
    if not root:
        log.error("must be run inside a git repo")
        sys.exit()
    os.chdir(root)

    # init docs
    if opts["docs"]:
        make_docs()

    # convert docstrings to rst
    if opts["rst"]:
        make_rst()

    # convert rst to html
    if opts["html"]:
        make_html()

def make_docs():
    docs = opts["--docs"]
    os.makedirs(docs, exist_ok=True)

    # index.rst and conf.py
    for f in ["index.rst", "conf.py"]:
        if not os.path.exists(f"{docs}/{f}"):
            shutil.copy(f"{TEMPLATES}/{f}", docs)

    # gitlab CI
    with open(f"{TEMPLATES}/.gitlab-ci.yml") as f:
        pages_ci = yaml.safe_load(f)
    if os.path.exists(".gitlab-ci.yml"):
        with open(".gitlab-ci.yml") as f:
            ci = yaml.safe_load(f)
        if "pages" not in ci:
            ci["pages"] = pages_ci["pages"]
    else:
        shutil.copy(f"{TEMPLATES}/.gitlab-ci.yml", ".gitlab-ci.yml")

def make_rst():
    docs = opts["--docs"]
    projects = opts.get("--projects")
    shutil.rmtree(f"{docs}/_rst", ignore_errors=True)

    # exclude folders that are not in git
    gitfiles = subprocess.run(["git", "ls-files"], check=True, capture_output=True, text=True).stdout.splitlines()
    gitfolders = [d[:d.rfind("/")] for d in gitfiles if d.find("/") >= 0]
    allfolders = [d[0].replace(os.path.sep, "/")[2:] for d in os.walk(".")]
    excluded = list(set(allfolders) - set(gitfolders))
    excluded = excluded + ignorefolders
    excluded.remove("")

    # get packages
    packages = []
    if not projects:
        projects = "."
    for project in projects.split(","):
        # top level packages
        packages.extend([p for p in find_packages(project) if p.find(".") < 0 and p not in excluded])
        if os.path.abspath(project) not in sys.path:
            sys.path.insert(0, project)

    for package in packages:
        cmd = shlex.split(f"sphinx-apidoc -f -o {docs}/_rst {package} {excluded}")
        subprocess.run(cmd)

def make_html():
    docs = opts["--docs"]
    shutil.rmtree(f"{docs}/_build", ignore_errors=True)

    cmd = shlex.split(f"sphinx-build -M html . _build")
    os.chdir(docs)
    subprocess.run(cmd)


def get_project_root(path=None):
    """ return project root folder where .git is located; or False if not in a git repo """
    if not path:
        path = os.getcwd()
    while True:
        if ".git" in os.listdir(path):
            return path
        old_path = path
        path = os.path.dirname(path)
        if path==old_path:
            return False

if __name__ == "__main__":
    main()
