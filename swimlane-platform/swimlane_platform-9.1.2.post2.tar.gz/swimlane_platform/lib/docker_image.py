from swimlane_platform.lib import debug_function_args, debug_function_return, names


class DockerImage:

    def __init__(self, repository=names.DEV_REPOSITORY, image_name=None, version=None):
        # type: (str, str, str) -> DockerImage
        self.repository = repository
        self.image_name = image_name
        self.version = version

    @debug_function_args
    def _parse(self, tag):
        # type: (str) -> None
        """
        Parses full tag to object properties.
        :param tag: The full tag.
        """
        tag = tag.replace(self.repository, '')
        self.image_name, self.version = tag.rsplit(':', 1)

    @staticmethod
    def parse(tag):
        # type: (str) -> DockerImage
        """
        Parses swimlane image tag and returns DockerImage
        :param tag: The full image value from docker-compose
        :return: DockerImage
        """
        docker_image = DockerImage()
        docker_image._parse(tag)
        return docker_image

    @debug_function_return
    @debug_function_args
    def get(self, is_dev):
        # type: (bool) -> str
        """
        Combines docker image tag parts together.
        :param is_dev: If image is pulled from development repository.
        :return: Full image tag.
        """
        return '{repository}{image}:{version}' \
            .format(repository=self.repository if is_dev else '', image=self.image_name, version=self.version)
