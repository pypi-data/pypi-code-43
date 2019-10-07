from typing import List, Optional
from PyVoice.MyDict import MyDict, DictProperty
from . import ImageDisplayOptions
from .Button import Button
from .Image import Image
from .OpenUrlAction import OpenUrlAction


class BasicCard(MyDict):
    """
    {
      "title": string,
      "subtitle": string,
      "formattedText": string,
      "image": {
        object(Image)
      },
      "buttons": [
        {
          object(Button)
        }
      ],
      "imageDisplayOptions": enum(ImageDisplayOptions),
    }
    """
    title: str = DictProperty('title', str)
    subtitle: str = DictProperty('subtitle', str)
    formatted_text: str = DictProperty('formattedText', str)
    image: Image = DictProperty('image', Image)
    buttons_list: List[Button] = DictProperty('buttons', list)
    image_display_options: ImageDisplayOptions = DictProperty('imageDisplayOptions', ImageDisplayOptions)

    def build(self, title: str = None, formatted_text: str = None, subtitle: str = None, image: Image = None,
              image_display_options: ImageDisplayOptions = None, *buttons: Button):

        self.buttons_list = []
        for item in buttons:
            assert isinstance(item, Button)
            self.buttons_list.append(item)

        if title is not None:
            self.title = title

        if formatted_text is not None:
            self.formatted_text = formatted_text

        if subtitle is not None:
            self.subtitle = subtitle

        if image is not None:
            self.image = image

        if image_display_options is not None:
            self.image_display_options = image_display_options

        return self

    def add_button(self, title: str, url: str) -> Button:
        button = Button().build(title=title, open_url_action=OpenUrlAction().build(url=url))
        self.buttons_list.append(button)

        return button

