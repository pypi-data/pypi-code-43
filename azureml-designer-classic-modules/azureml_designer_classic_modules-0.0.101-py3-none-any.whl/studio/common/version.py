from azureml.studio.core.utils.strutils import parse_version_str


class Version:
    """A class represents a semantic version."""

    __slots__ = ('major', 'minor', 'patch')

    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0):
        self.major = major
        self.minor = minor
        self.patch = patch
        self._do_the_metaphysical_check()

    @classmethod
    def parse(cls, string):
        return Version(*parse_version_str(string))

    @property
    def version_str(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self):
        return self.version_str

    def __eq__(self, other):
        if isinstance(other, Version):
            return self.version_str == other.version_str
        return NotImplemented

    def _do_the_metaphysical_check(self):
        if '4' in self.version_str:
            raise ValueError(f"Bad version '{self.version_str}': Should not contain '4'.")

        if 13 in (self.major, self.minor, self.patch):
            raise ValueError(f"Bad version '{self.version_str}': Should not contain '13'.")
