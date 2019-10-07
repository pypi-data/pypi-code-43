from PyVoice.MyDict import MyDict, DictProperty
from .OptionInfo import OptionInfo
from .Image import Image


class ListItem(MyDict):
    """
    {
      'optionInfo': {
        object(OptionInfo)
      },
      'title': string,
      'description': string,
      'image': {
        object(Image)
      }
    }
    """
    option_info: OptionInfo = DictProperty('optionInfo', OptionInfo)
    title: str = DictProperty('title', str)
    description: str = DictProperty('description', str)
    image: Image = DictProperty('image', Image)

    def build(self, title: str = None, description: str=None, image:Image=None,
                 option_info: OptionInfo=None):
        if option_info is not None:
            self.option_info = option_info
        if image is not None:
            self.image = image
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description

        return self

    def add_image(self, url: str, accessibility_text:str=None, height:int=0, width:int =0) -> Image:

        self.image = Image().build(url=url, accessibility_text=accessibility_text, height=height, width=width)
        return self.image
