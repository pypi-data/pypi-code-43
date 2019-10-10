class InvalidArgumentsError(Exception):
    def __init__(self, message: str):
        self.message = f"invalid arguments for Docker client: {message}"


class ImageNotFoundError(Exception):
    def __init__(self, tag):
        self.message = f"no image found for tag: {tag}"
