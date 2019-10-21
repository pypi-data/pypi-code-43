#
# Copyright (c) 2006-2019 Balabit
# All Rights Reserved.
#
import logging
from time import strftime
import re
import semantic_version
import yaml
from yaml.parser import ParserError


log = logging.getLogger(__name__)


class Manifest:
    def __init__(self, data, filename):
        self.data = data
        self.parsed = {}
        self.filename = filename
        self._check()

    @classmethod
    def from_file(cls, filename='MANIFEST'):
        try:
            with open(filename) as f:
                return cls.from_stream(f, filename)
        except FileNotFoundError:
            log.error("MANIFEST file not found, are we in a plugin folder?")
            raise

    @classmethod
    def from_stream(cls, stream, filename=None):
        try:
            return cls(yaml.safe_load(stream), filename)
        except ParserError:
            log.error("MANIFEST file format wrong, should be yaml")
            raise

    def _check(self, expected_type=('aa', 'credentialstore', 'signingca')):
        for field in ('name', 'api', 'version', 'description', 'entry_point', 'type'):
            if field not in self.data:
                raise RequiredFieldDoesNotExistError(field)
            if self.data[field] is None:
                raise RequiredFieldDoesNotExistError(field)
        if self.data['type'] not in expected_type:
            raise PluginTypeError('{} not in {}'.format(self.data['type'], expected_type))
        if not re.fullmatch('[a-zA-Z][a-zA-Z0-9_]+', self.name):
            raise NameFormatError(
                "MANIFEST name should start with letter and continue with letter, digit or underscore"
            )
        if not re.fullmatch('[A-Za-z0-9._-]+', self.entry_point):
            raise EntryPointFormatError(
                "MANIFEST entry point should only contain letters, digits, dot, dash or underscore"
            )
        if re.fullmatch('[0-9].*', str(self.version)):
            self.data['version'] = str(self.version)  # 0.9 would be float type
        else:
            raise VersionFormatError(
                "MANIFEST version should start with a digit"
            )

        self.parsed['api'] = semantic_version.Version(str(self.data['api']), partial=True)
        self.parsed['api'].patch = 0

    def check_api_version(self, plugin_sdk_version):
        api_v = self.parsed['api']
        sdk_v = semantic_version.Version(plugin_sdk_version)
        if not api_v <= sdk_v:
            raise ApiVersionError("MANIFEST api version may not be larger than Plugin SDK version")
        if not api_v.major == sdk_v.major:
            raise ApiVersionError("MANIFEST api major version must equal Plugin SDK major version")

    @property
    def api(self):
        return self.data['api']

    @property
    def entry_point(self):
        return self.data['entry_point']

    @property
    def name(self):
        return self.data['name']

    @property
    def type(self):
        return self.data['type']

    @property
    def version(self):
        return self.data['version']

    def make_snapshot_version(self):
        self.data['version'] = self.data['version'] + '-' + strftime("%Y%m%dT%H%M%S")

    def add_version_suffix(self, suffix):
        self.data['version'] = self.data['version'] + '-' + suffix.lstrip('-')

    def write_file(self):
        assert self.filename is not None
        with open(self.filename, "w") as f:
            yaml.dump(self.data, f, default_flow_style=False)


class RequiredFieldDoesNotExistError(AssertionError):
    pass


class PluginTypeError(AssertionError):
    pass


class ApiVersionError(AssertionError):
    pass


class NameFormatError(AssertionError):
    pass


class EntryPointFormatError(AssertionError):
    pass


class VersionFormatError(AssertionError):
    pass
