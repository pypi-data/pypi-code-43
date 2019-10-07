from PyVoice.MyDict import MyDict, DictProperty
from .SelectItemInfo import SelectItemInfo
from .Image import Image


class ListItem(MyDict):
    """
    {
      'info': {
        object(SelectItemInfo)
      },
      'title': string,
      'description': string,
      'image': {
        object(Image)
      }
    }
    """
    info: SelectItemInfo = DictProperty('info', SelectItemInfo)
    title: str = DictProperty('title', str)
    description: str = DictProperty('description', str)
    image: Image = DictProperty('image', Image)

    def build(self, title: str = None, description: str=None, image:Image=None,
              info: SelectItemInfo=None):
        if info is not None:
            self.info = info
        if image is not None:
            self.image = image
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description

        return self

    def add_info(self, key: str, *synonyms: str) -> SelectItemInfo:
        self.info = SelectItemInfo().build(key=key, *synonyms)
        return self.info

    def add_image(self, uri: str, accessibility_text:str=None) -> Image:

        self.image = Image().build(uri=uri, accessibility_text=accessibility_text)
        return self.image
