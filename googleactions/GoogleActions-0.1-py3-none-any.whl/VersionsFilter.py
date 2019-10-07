from PyVoice.MyDict import MyDict, DictProperty


class VersionsFilter(MyDict):
    """
    {
      'minVersion': number,
      'maxVersion': number
    }
    """

    min_version: int = DictProperty('minVersion', int)
    max_version: int = DictProperty('maxVersion', int)

    def build(self, min_version:int=None, max_version:int=None):
        self._min_version = min_version
        self._max_version = max_version

        return self
