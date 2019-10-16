from typing import Optional

import attr
import re


def convert_empty_tag(tag: Optional[str]) -> Optional[str]:
    if not tag:
        result = None
    else:
        result = tag
    return result


@attr.s(auto_attribs=True, frozen=True)
class Version(object):
    major: int
    minor: int
    patch: int
    tag: Optional[str] = attr.ib(converter=convert_empty_tag, default=None)

    def __str__(self):
        return self.to_string()

    @classmethod
    def from_string(cls, val: str):
        """ Create a Version object from a string of the form
        'major.minor.patch-tag', where the tag is optional.  If it is present,
        it must be separated from the rest of the string by a hyphen for this
        method to find it."""
        m = re.match(r'(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)'
                     r'(-(?P<tag>.+))?',
                     val)
        return cls(major=int(m.group('major')),
                   minor=int(m.group('minor')),
                   patch=int(m.group('patch')),
                   tag=m.group('tag'))

    def to_string(self) -> str:
        """ Create a version string of the form "major.min.patch-tag, where the
        hyphen and tag are only present if `self.tag != None` """
        version_str = "{0}.{1}.{2}".format(self.major, self.minor, self.patch)
        if self.tag:
            version_str += '-' + self.tag
        return version_str
