from ..abstracts import Version as AbstractedVersion
from ..converters import InternalUrl
from ..helpers import Dict, Download


class Version:
    """
    Compares the local with the upstream version.
    """

    def __init__(self):
        upstream_link = (
            "https://raw.githubusercontent.com/funilrys/PyFunceble/dev/version.yaml"
        )
        upstream_link = InternalUrl(upstream_link).to_right_version()

        self.upstream_data = Dict.from_yaml(Download(upstream_link).text())

    def check_force_update(self):
        """
        Checks if we need to force the user to update.
        """

        if "force_update" in self.upstream_data:
            for minimal in self.upstream_data["force_update"]["minimal_version"]:
                checked = AbstractedVersion.compare(minimal)
