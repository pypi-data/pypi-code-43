from marshmallow import Schema, fields, post_load
from pathlib import Path


class ProjectEntity:
    def __init__(self, name, project_repo, deploy_repo, workdir, metadir, env, active=False, docker_registry = None):
        self.name = name
        self.project_repo = project_repo
        self.deploy_repo = deploy_repo
        self.workdir = Path(workdir)
        self.metadir = Path(metadir)
        self.docker_registry = docker_registry
        self.env = env
        self.active = active


class StackEntity:
    def __init__(self, name, project_name, compose_directory, network="default", volumes=None):
        self.name = name
        self.project_name = project_name
        self.compose_directory = Path(compose_directory)
        self.compose_file = "{}.yml".format(self.name)
        self.network = network
        self.volumes = volumes


class UnitEntity:
    def __init__(self, name, project_name, stack_name, image_name=None, repo=None, codedir=None, working_dir=None,
                 branch=None):
        self.project_name = project_name
        self.name = name
        self.image_name = image_name
        self.repo = repo
        self.working_dir = working_dir  # working directory inside container
        self.stack_name = stack_name
        self.branch = branch
        try:
            self.codedir = Path(codedir)  # local code directory
        except:
            self.codedir = codedir

    @property
    def container_name(self):
        return ".".join(self.name.split(".")[1:])


class ProjectSchema(Schema):
    name = fields.Str()
    project_repo = fields.Str()
    deploy_repo = fields.Str()
    workdir = fields.Str()
    metadir = fields.Str()
    env = fields.Str()
    active = fields.Bool()
    docker_registry = fields.Str(missing=None)

    @post_load
    def make(self, data):
        return ProjectEntity(**data)


class StackSchema(Schema):
    name = fields.Str()
    project_name = fields.Str()
    compose_directory = fields.Str()
    network = fields.Str()
    volumes = fields.Dict(missing=None)

    @post_load
    def make(self, data):
        return StackEntity(**data)


class UnitSchema(Schema):
    name = fields.Str()
    image_name = fields.Str(missing=None)
    project_name = fields.Str()
    repo = fields.Str(missing=None)
    codedir = fields.Str(missing=None)
    working_dir = fields.Str(missing=None)
    stack_name = fields.Str()
    branch = fields.Str(missing=None)

    @post_load
    def make(self, data):
        return UnitEntity(**data)
