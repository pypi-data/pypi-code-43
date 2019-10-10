import json
from abc import ABC, abstractmethod
from typing import ForwardRef

import yaml

from . import exceptions


MODULE_PREFIX = "deploy_py.config."


class BaseConfig(ABC):
    def __repr__(self):
        return f"<{MODULE_PREFIX}{self.__class__.__name__}>"

    @abstractmethod
    def dict(self):
        pass

    def json(self, pretty=False):
        if pretty:
            return json.dumps(self.dict(), indent=4, sort_keys=True)
        return json.dumps(self.dict())


class DockerConfig(BaseConfig):
    def __init__(self, repo, creds="docker-credential-gcr", context="./", file="./Dockerfile"):
        self.creds = creds
        self.context = context
        self.file = file
        self.repo = repo

    def __repr__(self):
        return f"<{MODULE_PREFIX}DockerConfig: {self.repo}>"

    def dict(self):
        return {
            "creds": self.creds,
            "context": self.context,
            "file": self.file,
            "repo": self.repo,
        }


class HelmConfig(BaseConfig):
    def __init__(self, kind: str = "repo", chart_dir: str = "./deploy/{app}", namespace: str = "default",
                 dest_dir: str = "./deploy", save: bool = True, repo: str = "test", args: dict = None):
        if args is None:
            args = {}

        self.kind = kind
        self.chart_dir = chart_dir
        self.dest_dir = dest_dir
        self.save = save
        self.repo = repo
        self.args = args
        self.namespace = namespace

    def __repr__(self):
        return f"<{MODULE_PREFIX}HelmConfig: {self.chart_dir}>"

    def dict(self):
        return {
            "kind": self.kind,
            "chart_dir": self.chart_dir,
            "dest_dir": self.dest_dir,
            "save": self.save,
            "repo": self.repo,
            "args": self.args,
            "namespace": self.namespace,
        }


class Defaults:
    def __init__(self, project, context, docker, helm):
        self.project = project
        self.context = context
        self.docker = DockerConfig(**docker)
        self.helm = HelmConfig(**helm)


class Deployment(BaseConfig):
    def __init__(self, name: str, app: str, defaults: Defaults, project=None, context=None, docker=None, helm=None):
        if docker is None:
            docker = {}
        if helm is None:
            helm = {}

        self.name = name
        self.app = app
        self.project = project or defaults.project
        self.context = context or defaults.context
        self.docker = DockerConfig(
            repo=docker.get("repo", defaults.docker.repo),
            creds=docker.get("creds", defaults.docker.creds),
            context=docker.get("context", defaults.docker.context),
            file=docker.get("file", defaults.docker.file),
        )
        self.helm = HelmConfig(
            kind=helm.get("kind", defaults.helm.kind),
            chart_dir=helm.get("chart_dir", defaults.helm.chart_dir),
            dest_dir=helm.get("dest_dir", defaults.helm.dest_dir),
            save=helm.get("save", defaults.helm.save),
            repo=helm.get("repo", defaults.helm.repo),
            args=helm.get("args", defaults.helm.args),
            namespace=helm.get("namespace", defaults.helm.namespace),
        )

    def __repr__(self):
        return f"<{MODULE_PREFIX}Deployment: {self.name} for {self.app}>"

    def dict(self):
        return {
            "name": self.name,
            "app": self.app,
            "project": self.project,
            "context": self.context,
            "docker": self.docker.dict(),
            "helm": self.helm.dict(),
        }


class Config:
    def __init__(self, app: str, deployments: dict, defaults: dict = None):
        self.app = app
        self.defaults = Defaults(**defaults)
        self.deployments = {name: Deployment(name, app, self.defaults, **dep) for name, dep in deployments.items()}

    def __repr__(self):
        return f"<{MODULE_PREFIX}Config: {self.app}>"

    @classmethod
    def from_file(cls, path: str = ".deploy.yaml") -> ForwardRef("Config"):
        with open(path, "r") as conf_file:
            data = yaml.load(conf_file, Loader=yaml.SafeLoader)
        return Config(
            data["app"],
            deployments=data["deployments"],
            defaults=data.get("defaults", {})
        )

    def get_deployment(self, name: str) -> Deployment:
        try:
            return self.deployments[name]
        except KeyError:
            raise exceptions.DeploymentNotFoundError(name)
