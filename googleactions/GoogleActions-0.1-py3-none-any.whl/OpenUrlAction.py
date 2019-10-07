from PyVoice.MyDict import MyDict, DictProperty
from . import UrlTypeHint
from .AndroidApp import AndroidApp
from .VersionsFilter import VersionsFilter


class OpenUrlAction(MyDict):
    """
    {
      "url": string,
      "androidApp": {
        object(AndroidApp)
      },
      "urlTypeHint": enum(UrlTypeHint)
    }
    """
    
    url: str = DictProperty('url', str)
    android_app: AndroidApp = DictProperty('androidApp', AndroidApp)
    url_type_hint: UrlTypeHint = DictProperty('urlTypeHint', UrlTypeHint)

    def build(self, url: str=None, android_app:AndroidApp=None, type_hint:UrlTypeHint=None):
        if android_app is not None:
            self.android_app = android_app

        if type_hint is not None:
            self.url_type_hint = type_hint

        if url is not None:
            self.url = url
            
        return self

    def add_android_app(self, package_name: str, *versions_list) -> AndroidApp:
        self.android_app = AndroidApp(package_name=package_name, *versions_list)

        return self.android_app
