from .VersionsFilter import VersionsFilter
from PyVoice.MyDict import MyDict, DictProperty
from typing import List

class AndroidApp(MyDict):
    package_name: str = DictProperty('packageName', str)
    versions_list: List[VersionsFilter] = DictProperty('versions', list)

    def build(self, package_name: str=None, *versions_list):
        if package_name is not None:
            self.package_name = package_name

        if versions_list is not None:
            self.versions_list = versions_list
        else:
            self.versions_list = []

        return self

    def add_versions(self, *versions: VersionsFilter) -> List[VersionsFilter]:
        for item in versions:
            assert isinstance(item, VersionsFilter)
            self.versions_list.append(item)

        return self.versions_list

    def add_version(self, min_version: int = None, max_version: int = None) -> VersionsFilter:
        version_filter = VersionsFilter().build(min_version=min_version, max_version=max_version)
        self.versions_list.append(version_filter)

        return version_filter
