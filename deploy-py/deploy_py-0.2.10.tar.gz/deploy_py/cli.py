# -*- coding: utf-8 -*-

"""Console script for deploy_py."""
import sys
import click

from .config import Config
from .deploy_py import DeployClient
from . import docker


@click.group()
def deploy():
    """Console script for deploy_py."""
    pass


@deploy.command()
def version():
    click.echo("deploy_py v0.2.10")


@deploy.command("deploy")
@click.argument("release_type", type=click.Choice(['major', 'minor', "patch", "rebuild"]))
@click.argument("target")
@click.option("-f", "--file", "conf_path", default="./.deploy.yaml")
@click.option("-d", "--allow-dirty", is_flag=True, default=False)
@click.option("-v", "--verbosity", count=True)
@click.option("-n", "--dry-run", is_flag=True, default=False)
@click.option("--cleanup/--no-cleanup", is_flag=True, default=True)
def deploy_cmd(release_type, target, conf_path, allow_dirty, verbosity, dry_run, cleanup):
    dep = DeployClient(conf_path=conf_path, allow_dirty=allow_dirty, verbosity=verbosity)
    dep.deploy(release_type, target, dry_run=dry_run, do_cleanup=cleanup)


@deploy.group()
def docker():
    pass


@docker.command()
@click.argument("name")
@click.argument("version")
@click.option("-p", "--push", "do_push", is_flag=True, default=False)
def build(name, version, do_push):
    c = Config.from_file()
    deployment = c.get_deployment(name)
    d = docker.Client()
    tag = d.get_tag(repo=deployment.docker.repo, app=c.app, version=version)
    image, logs = d.build_image(deployment.docker.context, tag, push=do_push)
    click.echo(f"built image: {image}")


@docker.command()
@click.argument("tag")
def push(tag):
    d = docker.Client()
    d.push_image(tag)


@docker.command()
@click.argument("target")
@click.argument("field", required=False)
def get(target, field):
    c = Config.from_file()
    dep = c.get_deployment(target)
    if field:
        click.echo(getattr(dep.docker, field, None))
    else:
        click.echo(dep.docker.dict())


@deploy.group()
def helm():
    pass


@helm.command()
@click.argument("target")
@click.argument("field")
def get(target, field):
    c = Config.from_file()
    dep = c.get_deployment(target)
    click.echo(getattr(dep.helm, field, None))


if __name__ == "__main__":
    sys.exit(deploy())  # pragma: no cover
