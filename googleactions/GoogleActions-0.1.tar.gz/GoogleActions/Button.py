from PyVoice.MyDict import MyDict, DictProperty
from .OpenUrlAction import OpenUrlAction
from .AndroidApp import AndroidApp
from . import UrlTypeHint
from .VersionsFilter import VersionsFilter


class Button(MyDict):
    """
    {
      "title": string,
      "openUrlAction": {
        object(OpenUrlAction)
      },
    }
    """
    
    title: str = DictProperty('title', str)
    open_url_action: OpenUrlAction = DictProperty('openUrlAction', OpenUrlAction)

    def build(self, title: str=None, open_url_action: OpenUrlAction=None):
        if title is not None:
            self.title = title
        if open_url_action is not None:
            self.open_url_action = open_url_action

        return self

    def add_open_url_action(self, url: str = None, package_name: str = None, type_hint: UrlTypeHint = None,
                            *versions_list: VersionsFilter):

        self.open_url_action = OpenUrlAction().build(url=url, android_app=AndroidApp().build(package_name=package_name,
                                                                                        *versions_list)
                                                , type_hint=type_hint)

        return self.open_url_action
