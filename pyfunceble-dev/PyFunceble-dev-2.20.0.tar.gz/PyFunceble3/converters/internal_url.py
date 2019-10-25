from ..abstracts import Version
from ..exceptions import WrongParameterType


class InternalUrl:
    """
    Converter of the internal URLs.

    .. note::
        The internal URLs are actually the URL that has nothing to
        do with what we are going to test.

        They are only relevant for the software itself.

    :param str url: The URL to convert.
    """

    def __init__(self, url):

        if not isinstance(url, str):
            raise WrongParameterType(f"<url> should be {str}, {type(url)} given.")

        self.url = url

    def to_right_version(self):
        """
        Process the conversion to the right URL.
        """

        if Version.is_local_dev():
            return self.url.replace("master", "dev")
        return self.url.replace("dev", "master")
