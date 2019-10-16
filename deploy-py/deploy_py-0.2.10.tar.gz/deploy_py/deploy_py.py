# -*- coding: utf-8 -*-
from typing import Generator

from bumpv import BumpClient

from . import docker
from . import exceptions
from . import helm
from .config import Config, HelmConfig
from .logging import get_logger


class DeployClient:
    def __init__(self, conf_path: str = ".deploy.yaml", allow_dirty: bool = False, verbosity: int = 0):
        self.logger = get_logger(level=verbosity)
        self.config = Config.from_file(conf_path)
        self.bumpv = BumpClient(allow_dirty=allow_dirty)
        self.docker = docker.Client(verbosity=verbosity)
        self.helm = helm.Client(verbosity=verbosity)

    def deploy(self, release_type: str, target: str, do_cleanup: bool = True, dry_run: bool = False):
        self.logger.debug(
            f"ARGS:\n\trelease_type={release_type}\n\ttarget={target}\n\tdo_cleanup={do_cleanup}\n\tdry_run={dry_run}"
        )
        deployment = self.config.get_deployment(target)
        self.logger.debug(f"got deployment {deployment}")
        self.logger.debug(f"deployment info:\n{deployment.json(pretty=True)}")

        if do_cleanup:
            previous_tag = self.docker.get_tag(
                repo=deployment.docker.repo,
                app=self.config.app,
                version=self.bumpv.current_version.serialize()
            )
            self.cleanup(target, previous_tag)

        if release_type == "rebuild":
            version = self.bumpv.current_version
        else:
            version = self.bumpv.bump(release_type, dry_run)

        self.logger.debug(f"starting {release_type} release for {deployment.app}")

        docker_tag = self.docker.get_tag(repo=deployment.docker.repo, app=self.config.app, version=version.serialize())
        image, _ = self.build_image(deployment.docker.context, docker_tag, quiet=False)
        if image is None:
            return
        self.package(
            self.config.app,
            version.serialize(),
            config=deployment.helm,
            dry_run=dry_run
        )
        resp, success = self.helm.update_release(
            name=self.config.app,
            version=version.serialize(),
            app_namespace=deployment.helm.namespace,
            chart_path=deployment.helm.chart_dir,
            kind=helm.ChartKinds.directory,
            context=deployment.context,
            dry_run=dry_run,
            values=deployment.helm.args
        )
        if success and not dry_run:
            self.update_helm_repo(deployment.helm.chart_dir, deployment.helm.repo)
        elif not success:
            raise exceptions.DeploymentFailedError("helm update failed")

    def build_image(self, build_ctx: str, tag: str, push: bool = True, **kwargs) -> (docker.Image, Generator):
        try:
            return self.docker.build_image(build_ctx, tag, push, **kwargs)
        except self.docker.BuildError as err:
            self.logger.error(err.build_log)

    def cleanup(self, target: str, previous_tag: str):
        self.logger.debug(f"cleaning up previous build artifacts for {target}; previous tag: {previous_tag}")
        deployment = self.config.get_deployment(target)
        self.helm.delete_chart(deployment.helm.repo, self.config.app, self.bumpv.current_version.serialize())

        try:
            self.docker.delete_image(previous_tag)
        except self.docker.ImageNotFound as err:
            self.logger.warn(f"error deleting previous image: {err}")
            return None, None

    def package(self, app: str, version: str, chart_dir: str = None,
                dest_dir: str = None, repo: str = None, config: HelmConfig = None, dry_run=False) -> str:
        if config is not None:
            chart_dir = config.chart_dir
            dest_dir = config.dest_dir
            repo = config.repo

        chart_path = self.helm.package(
            app,
            version,
            chart_dir,
            dest_dir
        )

        if not dry_run:
            self.helm.upload(repo, chart_path)
        return chart_path

    def update_helm_repo(self, chart_dir: str, repo_name: str):
        self.helm.update_index(chart_dir, repo_name)
