from PyVoice.MyDict import MyDict, DictProperty
from .Image import Image


class MediaObject(MyDict):
    """
    {
      "name": string,
      "description": string,
      "contentUrl": string,

      // Union field image can be only one of the following:
      "largeImage": {
        object(Image)
      },
      "icon": {
        object(Image)
      }
      // End of list of possible types for union field image.
    }
    """
    name: str = DictProperty('name', str)
    description: str = DictProperty('description', str)
    content_url: str = DictProperty('contentUrl', str)
    large_image: Image = DictProperty('largeImage', Image)
    icon: Image = DictProperty('icon', Image)

    def build(self, name: str, description: str = None, content_url: str = None,
                 large_image: Image = None,
                 icon: Image = None):

        self.name = name
        if description is not None:
            self.description = description
        if content_url is not None:
            self.content_url = content_url

        if large_image is not None:
            self.large_image = large_image

        if icon is not None:
            self.icon = icon

        return self

    def add_large_image(self, url: str, text: str=None, height:int = 0, width:int =0) -> Image:
        self.large_image = Image().build(url=url, accessibility_text=text, height=height, width=width)

        return self.large_image

    def add_icon(self, url: str, text: str = None, height: int = 0, width: int = 0) -> Image:
        self.icon = Image().build(url=url, accessibility_text=text, height=height, width=width)

        return self.icon
