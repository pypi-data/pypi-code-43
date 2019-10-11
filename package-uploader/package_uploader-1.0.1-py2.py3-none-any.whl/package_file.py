import enum
import os
import re
from dataclasses import dataclass

from wheel.bdist_wheel import safer_name, safer_version

from .exceptions import NoDistFilesFoundError


class DistType(enum.Enum):
    SDIST = "Source Distribution"
    WHEEL = "Wheel distribution"


@dataclass
class DistFile:
    file: os.DirEntry
    dist_type: DistType
    version: str
    package: str

    @property
    def name(self):
        return self.file.name

    @property
    def basename(self):
        return self.name

    @property
    def path(self):
        return self.file.path

    @property
    def type_display(self):
        return self.dist_type.value


# stolen from bdist_wheel command
def wheel_dist_name(package_meta):
    """Return distribution full name with - replaced with _"""
    components = (safer_name(package_meta.get_name()),
                  safer_version(package_meta.get_version()))
    # currently no support for wheel packages with build number component
    return '-'.join(components)


def discover_dists(package_meta):
    no_files = True
    if not os.path.isdir(os.path.abspath('dist/')):
        raise NoDistFilesFoundError(
            "`dist` directory doesn't exist for %s, (version: %s). Please check that specified version was built.",
            package_meta.get_name(),
            package_meta.get_version(),
        )
    for file in os.scandir(os.path.abspath('dist/')):
        if not file.is_file():
            continue
        dist_type = detect_dist_file(file.name, package_meta)
        if dist_type is None:
            continue
        no_files = False
        yield DistFile(
            file=file, dist_type=dist_type, version=package_meta.get_version(), package=package_meta.get_name(),
        )
    if no_files:
        raise NoDistFilesFoundError(
            'No dist files found for %s, (version: %s).Please check that specified version was built.',
            package_meta.get_name(),
            package_meta.get_version(),
        )


def detect_dist_file(name, package_meta):
    if (
            name.endswith('.tar')
            or name.endswith('.tar.gz')
            or name.endswith('.tar.bz2')
            or name.endswith('.tar.Z')
            or name.endswith('.zip')
    ):
        # sdist package
        package_name = package_meta.get_fullname()
        if re.match(
            fr'''
                {re.escape(package_name)}           # File name with version
                \.(?:tar(?:\.(?:gz|bz2|Z))?|zip)    # Extension
            ''',
            name, re.IGNORECASE | re.VERBOSE,
        ):
            return DistType.SDIST
    elif name.endswith('.whl'):
        # bdist wheel package
        package_name = wheel_dist_name(package_meta)
        if re.match(
                fr'''
                {re.escape(package_name)}           # File name with version
                -[^-]+                              # Compatible Python version
                -[^-]+                              # Compatible ABI version
                -[^-]+                              # Compatible Platform
                \.whl                               # Extension
                ''',
                name, re.IGNORECASE | re.VERBOSE,
        ):
            return DistType.WHEEL
    # Currently no support for any other package type
    return None
