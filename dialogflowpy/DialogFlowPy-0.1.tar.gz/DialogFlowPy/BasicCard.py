from typing import List, Optional
from PyVoice.MyDict import MyDict, DictProperty
from .Button import Button
from .Image import Image
from .OpenUriAction import OpenUriAction


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
    }
    """
    title: str = DictProperty('title', str)
    subtitle: str = DictProperty('subtitle', str)
    formatted_text: str = DictProperty('formattedText', str)
    image: Image = DictProperty('image', Image)
    buttons_list: List[Button] = DictProperty('buttons', list)

    def build(self, title: str = None, formatted_text: str = None, subtitle: str = None, image: Image = None,
              *buttons: Button):

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

        return self

    def add_button(self, title: str, uri: str) -> Button:
        button = Button().build(title=title, open_uri_action=OpenUriAction().build(uri=uri))
        self.buttons_list.append(button)

        return button
