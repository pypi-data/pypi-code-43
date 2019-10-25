from swimlane_platform.lib import BaseWithLog
from abc import abstractproperty, ABCMeta, abstractmethod
import semver
from future.utils import with_metaclass


class UpgradeStep(with_metaclass(ABCMeta, BaseWithLog)):

    @abstractproperty
    def FROM(self):
        # type: () -> semver.VersionInfo
        pass

    @abstractproperty
    def TO(self):
        # type: () -> semver.VersionInfo
        pass

    @abstractmethod
    def process(self):
        # type: () -> None
        pass
