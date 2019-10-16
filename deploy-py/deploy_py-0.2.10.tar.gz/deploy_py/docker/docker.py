import json
from typing import Generator

import docker
import requests
from docker.errors import ImageNotFound, BuildError
from docker.models.images import Image

from . import exceptions
from ..logging import get_logger


DEFAULT_BASIC_TAG_TEMPLATE = "{app}:{version}"
DEFAULT_REPO_TAG_TEMPLATE = "{repo}/{app}:{version}"
MODULE_PREFIX = "deploy.docker."


class Client:
    ImageNotFound = exceptions.ImageNotFoundError
    BuildError = BuildError

    def __init__(self, verbosity: int = 0):
        self.logger = get_logger(f"{MODULE_PREFIX}Client", verbosity)
        self.docker = docker.from_env()

    def __repr__(self):
        return f"<{MODULE_PREFIX}Client>"

    @staticmethod
    def get_tag(template: str = DEFAULT_REPO_TAG_TEMPLATE, **kwargs):
        return template.format(**kwargs)

    def _format_build_log(self, build_log):
        results = []
        for line in build_log:
            parsed = json.loads(line.split(b"\r\n")[0])
            results.append(parsed.get("stream", parsed.get("errorDetail")))
        return "\n.".join(results)

    def build_image(self, build_ctx: str, tag: str, push: bool = False, **kwargs) -> (Image, Generator):
        self.logger.info(f"building image with tag {tag}")
        try:
            image, logs = self.docker.images.build(
                path=build_ctx,
                tag=tag,
                buildargs=kwargs.get("buildargs", None),
                cache_from=kwargs.get("cache_from", None),
                container_limits=kwargs.get("container_limits", None),
                custom_context=kwargs.get("custom_context", False),
                decode=kwargs.get("decode", False),
                dockerfile=kwargs.get("dockerfile", None),
                encoding=kwargs.get("encoding", None),
                extra_hosts=kwargs.get("extra_hosts", None),
                forcerm=kwargs.get("forcerm", True),
                gzip=kwargs.get("gzip", False),
                isolation=kwargs.get("isolation", None),
                labels=kwargs.get("labels", None),
                network_mode=kwargs.get("network_mode", None),
                nocache=kwargs.get("nocache", False),
                platform=kwargs.get("platform", None),
                pull=kwargs.get("pull", False),
                quiet=kwargs.get("quiet", False),
                rm=kwargs.get("rm", False),
                shmsize=kwargs.get("shmsize", None),
                squash=kwargs.get("squash", None),
                target=kwargs.get("target", None),
                timeout=kwargs.get("timeout", None),
                use_config_proxy=kwargs.get("use_config_proxy", True)
            )

            if push:
                self.logger.info(f"pushing image with tag {tag}")
                self.push_image(tag)

            return image, logs
        except BuildError as err:
            err.build_log = self._format_build_log(err.build_log)

    def push_image(self, tag: str, stream: bool = False, decode: bool = False):
        self.docker.images.push(tag, stream=stream, decode=decode)

    def delete_image(self, image: str, force: bool = False, noprune: bool = False):
        self.logger.info(f"deleting image: {image}")
        try:
            self.docker.images.remove(image, force=force, noprune=noprune)
        except ImageNotFound:
            raise exceptions.ImageNotFoundError(image)
        except requests.exceptions.ConnectionError as err:
            self.logger.error(f"ERR: {err.response}")

    def image_exists(self, image: str):
        image = self.docker.images.get(image)

    def image_ids_match(self, ):
        pass
